"""
Lineage Lens - Streamlit Application
Main entry point for the data lineage analysis platform
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

from src.lineage_lens.parsers.sql_parser import SQLLineageParser
from src.lineage_lens.visualizers.graph_visualizer import LineageGraphVisualizer
from src.lineage_lens.visualizers.cytoscape_visualizer import CytoscapeGraphVisualizer
from src.lineage_lens.visualizers.simple_graph_visualizer import SimpleGraphVisualizer
from src.lineage_lens.llm.claude_explainer import ClaudeLineageExplainer
from src.lineage_lens.models.lineage_models import LineageQuery

try:
    from src.lineage_lens.utils.config import settings
except ImportError:
    # Fallback if config import fails
    class MockSettings:
        page_title = "🔍 Lineage Lens"
        page_icon = "🔍"
        layout = "wide"
    settings = MockSettings()


def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=settings.page_title,
        page_icon=settings.page_icon,
        layout=settings.layout,
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
            border: 1px solid #e0e0e0;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4;
            color: white;
        }
        
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
        }
        
        .stPlotlyChart {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'lineage_graph' not in st.session_state:
        st.session_state.lineage_graph = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('ANTHROPIC_API_KEY', '')
    if 'layout_option' not in st.session_state:
        st.session_state.layout_option = 'hierarchical'


def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        st.title("📁 File Upload")
        
        # API Key input - only show if not set in environment
        if st.session_state.api_key:
            st.success("✅ API Key configured")
            if st.button("🔄 Change API Key"):
                st.session_state.show_api_input = True
        else:
            st.warning("⚠️ API Key required for AI features")
            
        if not st.session_state.api_key or getattr(st.session_state, 'show_api_input', False):
            api_key = st.text_input(
                "Claude API Key",
                type="password",
                help="Enter your Anthropic Claude API key",
                value="",
                key="claude_api_key"
            )
            
            if api_key:
                st.session_state.api_key = api_key
                os.environ['ANTHROPIC_API_KEY'] = api_key
                st.session_state.show_api_input = False
                st.rerun()
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload SQL Files",
            type=['sql', 'txt'],
            accept_multiple_files=True,
            help="Upload SQL scripts to analyze data lineage"
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            
            if st.button("🔍 Analyze Lineage", type="primary"):
                analyze_uploaded_files()
        
        # Analysis options
        st.divider()
        st.subheader("🎛️ Visualization Options")
        
        layout_options = ["hierarchical", "spring", "circular", "kamada_kawai"]
        current_index = layout_options.index(st.session_state.layout_option) if st.session_state.layout_option in layout_options else 0
        
        layout_option = st.selectbox(
            "Graph Layout",
            layout_options,
            index=current_index,
            help="Choose how to arrange the nodes in the graph",
            key="layout_selection"
        )
        st.session_state.layout_option = layout_option
        
        # Layout descriptions
        layout_descriptions = {
            "hierarchical": "📊 Professional pipeline layout (Recommended)", 
            "spring": "🌸 Natural spring-force layout",
            "circular": "⭕ Circular arrangement",
            "kamada_kawai": "🎯 Force-directed optimal layout"
        }
        
        if layout_option in layout_descriptions:
            st.caption(layout_descriptions[layout_option])
        
        # Statistics
        if st.session_state.lineage_graph:
            st.divider()
            st.subheader("📊 Statistics")
            visualizer = LineageGraphVisualizer()
            stats = visualizer.create_summary_stats(st.session_state.lineage_graph)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Tables", stats["total_tables"])
                st.metric("Source Tables", stats["source_tables"])
            with col2:
                st.metric("Target Tables", stats["target_tables"])
                st.metric("Connections", stats["total_connections"])


def analyze_uploaded_files():
    """Analyze uploaded SQL files and extract lineage"""
    if not st.session_state.uploaded_files:
        st.error("Please upload SQL files first")
        return
    
    try:
        with st.spinner("Analyzing SQL files..."):
            parser = SQLLineageParser()
            
            # Combine all uploaded file contents
            combined_sql = ""
            total_size = 0
            
            for uploaded_file in st.session_state.uploaded_files:
                content = uploaded_file.read().decode('utf-8')
                total_size += len(content)
                combined_sql += f"\\n-- File: {uploaded_file.name}\\n{content}\\n"
            
            # Check file size to prevent 400 errors
            if total_size > 50000:  # 50KB limit to prevent AxiosError 400
                st.error(f"""
                🚨 **File Too Large**: {total_size:,} characters detected.
                
                **This will likely cause AxiosError 400. Solutions:**
                1. **Split large files** into smaller SQL scripts (< 50KB each)
                2. **Remove comments** and whitespace to reduce size  
                3. **Test with simpler datasets** first
                4. **Upload files individually** instead of all at once
                
                Large payloads overwhelm Streamlit's visualization components.
                """)
                return
            
            # Parse SQL and extract lineage
            lineage_graph = parser.parse_sql_file(combined_sql)
            st.session_state.lineage_graph = lineage_graph
            
            st.success(f"✅ Analyzed {len(st.session_state.uploaded_files)} files successfully!")
            st.info(f"📊 Found {len(lineage_graph.tables)} tables in your pipeline")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error analyzing files: {str(e)}")
        if "400" in str(e):
            st.error("🔍 This appears to be a 400 Bad Request error. Possible causes:")
            st.markdown("""
            - File content too large for API processing
            - Invalid characters in SQL file
            - API rate limiting or quota exceeded
            - Network connectivity issues
            """)
            st.info("💡 Try uploading a smaller SQL file or check your API configuration.")


def render_main_content():
    """Render the main application content"""
    st.title("🔍 Lineage Lens")
    st.markdown("*Intelligent Data Lineage Analysis Platform*")
    
    if not st.session_state.lineage_graph:
        render_welcome_screen()
    else:
        render_analysis_results()


def render_welcome_screen():
    """Render welcome screen when no data is loaded"""
    st.markdown("""
    ### Welcome to Lineage Lens! 👋
    
    This platform helps you understand data lineage and dependencies in your SQL pipelines.
    
    **Getting Started:**
    1. 🔑 Enter your Claude API key in the sidebar
    2. 📁 Upload your SQL files using the file uploader
    3. 🔍 Click "Analyze Lineage" to extract dependencies
    4. 💬 Ask questions about your data flow
    
    **What you can do:**
    - 📊 Visualize table dependencies as interactive graphs
    - 🤖 Ask natural language questions about data lineage
    - 🔄 Understand data transformations and flow
    - 📈 Get insights into pipeline complexity
    """)
    
    # Sample questions
    st.subheader("💡 Example Questions You Can Ask:")
    example_questions = [
        "Where does the sales_summary table get its data from?",
        "What tables depend on customer_data?",
        "How does data flow from raw tables to final reports?",
        "Which tables are at the beginning of my pipeline?",
        "What transformations happen to user data?"
    ]
    
    for question in example_questions:
        st.markdown(f"• *{question}*")


def render_analysis_results():
    """Render analysis results with visualization and chat interface"""
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Visualization", "💬 Ask Questions", "📋 Details"])
    
    with tab1:
        render_visualization_tab()
    
    with tab2:
        render_chat_tab()
    
    with tab3:
        render_details_tab()


def render_visualization_tab():
    """Render the lineage visualization with professional Cytoscape.js"""
    if not st.session_state.lineage_graph:
        st.warning("📊 No lineage data available. Please upload and analyze a SQL file first.")
        return

    try:
        # Visualization type selector
        viz_type = st.selectbox(
            "🎨 Visualization Type",
            ["Simple & Reliable (SVG)", "Professional (Cytoscape.js)", "Classic (Plotly)"],
            index=0,
            help="Choose your preferred visualization style",
            key="visualization_type"
        )
        
        if viz_type == "Simple & Reliable (SVG)":
            # Use simple, reliable SVG visualizer
            simple_visualizer = SimpleGraphVisualizer()
            
            st.subheader("📊 Simple Data Lineage Graph")
            st.info("💡 **Reliable visualization**: Hover over nodes for details, works offline!")
            
            # Dynamic height based on graph complexity to prevent 400 errors
            table_count = len(st.session_state.lineage_graph.tables)
            
            if table_count > 15:
                # Large datasets - minimal height to prevent 400 error
                height = 500
                st.warning("⚠️ Large dataset detected. Using minimal view to prevent AxiosError 400.")
            elif table_count > 8:
                # Medium datasets (like 12-table e-commerce) - conservative height
                height = 600
                st.info("📊 Medium dataset. Using optimized view to prevent errors.")
            else:
                # Small datasets - full height
                height = 650
            
            stats = simple_visualizer.render_in_streamlit(
                st.session_state.lineage_graph,
                height=height
            )
            
            # Display compact statistics below the graph (for Simple)
            st.markdown("---")
            st.markdown("### 📈 Lineage Statistics")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📊 Total Tables", stats['total_tables'])
            
            with col2:
                st.metric("🟢 Source Tables", stats['source_tables'])
            
            with col3:
                st.metric("🔵 Intermediate", stats['intermediate_tables'])
            
            with col4:
                st.metric("🔴 Target Tables", stats['target_tables'])
                
            with col5:
                st.metric("🔗 Relationships", stats['total_relationships'])
            
        elif viz_type == "Professional (Cytoscape.js)":
            # Use new Cytoscape visualizer
            cytoscape_visualizer = CytoscapeGraphVisualizer()
            layout = getattr(st.session_state, 'layout_option', 'dagre')
            
            st.subheader("🔍 Interactive Data Lineage Graph")
            st.info("💡 **Pro tip**: Hover over nodes for details, click to highlight connections, use controls to change layout!")
            
            # Render the professional Cytoscape visualization
            stats = cytoscape_visualizer.render_in_streamlit(
                st.session_state.lineage_graph,
                layout_algorithm=layout,
                height=650
            )
            
            # Display statistics below the graph (for Cytoscape)
            st.markdown("---")
            st.markdown("### 📈 Lineage Statistics")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📊 Total Tables", stats['total_tables'])
            
            with col2:
                st.metric("🟢 Source Tables", stats['source_tables'])
            
            with col3:
                st.metric("🔵 Intermediate", stats['intermediate_tables'])
            
            with col4:
                st.metric("🔴 Target Tables", stats['target_tables'])
                
            with col5:
                st.metric("🔗 Relationships", stats['total_relationships'])
            
        else:
            # Use classic Plotly visualizer
            st.subheader("📊 Classic Data Lineage Graph")
            visualizer = LineageGraphVisualizer()
            layout = getattr(st.session_state, 'layout_option', 'hierarchical')

            # Create larger, more visually appealing graph
            fig = visualizer.create_plotly_visualization(
                st.session_state.lineage_graph,
                layout_algorithm=layout
            )
            
            # Make the graph much larger and more prominent
            st.plotly_chart(fig, use_container_width=True, height=700)
            
            # Summary statistics in a more compact layout
            stats = visualizer.create_summary_stats(st.session_state.lineage_graph)
            
            st.markdown("---")
            st.markdown("### 📈 Pipeline Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Tables", stats["total_tables"])
            with col2:
                st.metric("🟢 Source Tables", stats["source_tables"])
            with col3:
                st.metric("🔴 Target Tables", stats["target_tables"])
            with col4:
                st.metric("🔗 Connections", stats["total_connections"])
            
            # Additional insights
            if stats["total_tables"] > 0:
                col1, col2 = st.columns(2)
                with col1:
                    complexity = "High" if stats["complexity_score"] > 50 else "Medium" if stats["complexity_score"] > 20 else "Low"
                    st.metric("🧮 Complexity", complexity, f"{stats['complexity_score']}/100")
                with col2:
                    st.metric("📏 Max Depth", f"{stats['max_depth']} levels")

    except Exception as e:
        st.error(f"❌ Error creating visualization: {str(e)}")
        st.error("Please check that your SQL file contains valid CREATE statements.")
        st.info("💡 Try uploading a different SQL file or check the format of your SQL statements.")


def render_chat_tab():
    """Render the chat interface for lineage questions"""
    st.subheader("💬 Ask Questions About Your Data Lineage")
    
    # Check if API key is available
    if not os.getenv('ANTHROPIC_API_KEY'):
        st.warning("⚠️ Please enter your Claude API key in the sidebar to use the chat feature")
        return
    
    try:
        explainer = ClaudeLineageExplainer()
        
        # Suggested questions
        suggestions = explainer.suggest_questions(st.session_state.lineage_graph)
        
        st.markdown("### 💡 Suggested Questions")
        st.markdown("*Click any question below to get instant insights about your data pipeline:*")
        
        # Better layout for suggestions
        for i, suggestion in enumerate(suggestions):
            if st.button(f"❓ {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                process_user_question(suggestion, explainer)
            if i < len(suggestions) - 1:  # Add small spacing between buttons
                st.markdown("")
        
        st.divider()
        st.markdown("### 💭 Ask Your Question")
        
        # Chat input with better styling
        with st.container():
            user_question = st.text_area(
                "Ask a question about your data lineage:",
                placeholder="e.g., Where does sales_total come from?\nHow does data flow from raw tables to reports?\nWhat tables depend on customer_data?",
                height=80,
                help="Ask any question about your data pipeline, table relationships, or data flow"
            )
            
            # Center the send button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚀 Send Question", type="primary", use_container_width=True) and user_question:
                    process_user_question(user_question, explainer)
        
        # Display chat history with better formatting
        if st.session_state.chat_history:
            st.divider()
            st.subheader("💭 Conversation History")
            
            for i, (question, answer) in enumerate(reversed(st.session_state.chat_history[-5:])):
                with st.expander(f"Q: {question}", expanded=(i == 0)):
                    # Use container for better spacing
                    with st.container():
                        st.markdown("**Answer:**")
                        # Use full width for answer
                        st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            padding: 15px;
                            border-radius: 8px;
                            border-left: 4px solid #007bff;
                            margin: 10px 0;
                            font-size: 14px;
                            line-height: 1.6;
                        ">
                        {answer}
                        </div>
                        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error initializing chat: {str(e)}")


def process_user_question(question: str, explainer: ClaudeLineageExplainer):
    """Process user question and generate response"""
    try:
        with st.spinner("Generating response..."):
            query = LineageQuery(query_text=question)
            explanation = explainer.explain_lineage(st.session_state.lineage_graph, query)
            
            # Add to chat history
            st.session_state.chat_history.append((question, explanation.explanation))
            
            # Display response with better formatting
            st.success("✅ Response generated!")
            
            # Use full-width container for the answer
            with st.container():
                st.markdown("**Answer:**")
                st.markdown(f"""
                <div style="
                    background-color: #e8f5e8;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #28a745;
                    margin: 15px 0;
                    font-size: 15px;
                    line-height: 1.7;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                {explanation.explanation}
                </div>
                """, unsafe_allow_html=True)
                
                if explanation.affected_tables:
                    st.markdown(f"""
                    <div style="
                        background-color: #fff3cd;
                        padding: 12px 20px;
                        border-radius: 8px;
                        border-left: 4px solid #ffc107;
                        margin: 10px 0;
                        font-size: 14px;
                    ">
                    <strong>🔗 Related Tables:</strong> {', '.join(explanation.affected_tables)}
                    </div>
                    """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error generating response: {str(e)}")
        
        # Provide specific help for common errors
        if "400" in str(e):
            st.error("🔍 API Request Error (400 Bad Request)")
            st.markdown("""
            **Possible causes:**
            - API key invalid or expired
            - Request payload too large
            - Model name not supported
            - Endpoint configuration issue
            
            **Quick fixes:**
            - Check your API key in the sidebar
            - Try asking a shorter question
            - Verify your Rakuten API access
            """)
        elif "401" in str(e):
            st.error("🔐 Authentication Error (401 Unauthorized)")
            st.markdown("Please check your API key in the sidebar.")
        elif "403" in str(e):
            st.error("🚫 Access Forbidden (403 Forbidden)")
            st.markdown("""
            **Your API key is valid but lacks permissions:**
            - Check if your Rakuten API key has access to Claude models
            - Verify the model `claude-sonnet-4-20250514` is available to your account
            - Ensure your API key has chat completion permissions
            - Check if you've exceeded rate limits or quotas
            - Contact Rakuten support if permissions appear correct
            
            **Quick troubleshooting:**
            - Try a different model name in your .env file
            - Check your Rakuten console for API status
            - Verify your account is active and has sufficient credits
            """)
        elif "404" in str(e):
            st.error("🔍 Endpoint Not Found (404)")
            st.markdown("The API endpoint might be incorrect. Check your configuration.")
        elif "timeout" in str(e).lower():
            st.error("⏱️ Request Timeout")
            st.markdown("The API request took too long. Try asking a simpler question.")


def render_details_tab():
    """Render detailed lineage information"""
    st.subheader("📋 Detailed Lineage Information")
    
    if not st.session_state.lineage_graph:
        st.warning("No lineage data available")
        return
    
    # Table details
    for table_name, table_info in st.session_state.lineage_graph.tables.items():
        with st.expander(f"📊 {table_name} ({table_info.table_type.value})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Upstream Dependencies:**")
                if table_info.upstream_tables:
                    for upstream in table_info.upstream_tables:
                        st.markdown(f"• {upstream}")
                else:
                    st.markdown("*No upstream dependencies*")
            
            with col2:
                st.markdown("**Downstream Dependencies:**")
                if table_info.downstream_tables:
                    for downstream in table_info.downstream_tables:
                        st.markdown(f"• {downstream}")
                else:
                    st.markdown("*No downstream dependencies*")
            
            if table_info.columns:
                st.markdown("**Columns:**")
                for col in table_info.columns:
                    st.markdown(f"• {col.column_name} ({col.transformation_type or 'direct'})")
            
            if table_info.sql_query:
                st.markdown("**SQL Query:**")
                st.code(table_info.sql_query, language="sql")


def main():
    """Main application entry point"""
    configure_page()
    initialize_session_state()
    
    # Render application
    render_sidebar()
    render_main_content()
    
    # Footer
    st.divider()
    st.markdown("*Built with ❤️ for the Mindstream Hackathon*")


if __name__ == "__main__":
    main()

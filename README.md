# 🔍 Lineage Lens

**Intelligent Data Lineage Analysis Platform**

Lineage Lens is an AI-powered platform that automatically extracts and explains data lineage from SQL scripts, providing interactive visualizations and natural language explanations to help data teams understand complex data flows.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for React frontend)
- Claude API key from Anthropic

### Choose Your Interface

#### Option 1: React Frontend (Recommended)
```bash
cd Mindstream_Maker/react-frontend
./run_react.sh
```

#### Option 2: Streamlit Backend
```bash
cd Mindstream_Maker/code
./run_app.sh
```

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd Mindstream_Maker/code
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: Requirements use flexible version ranges (>=) to avoid dependency conflicts and ensure compatibility with your existing Python environment.*

3. **Set up environment:**
   ```bash
   # Copy environment template
   cp config/env_example.txt .env
   
   # Edit .env and add your Claude API key
   echo "ANTHROPIC_API_KEY=your_api_key_here" >> .env
   ```

4. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser to:** `http://localhost:8501`

## 📁 Project Structure

```
Lineage_Lens/
├── code/
│   ├── src/
│   │   ├── lineage_lens/
│   │   │   ├── models/          # Pydantic data models
│   │   │   ├── parsers/         # SQL parsing logic
│   │   │   ├── visualizers/     # Graph visualization
│   │   │   ├── llm/             # Claude API integration
│   │   │   └── utils/           # Configuration & utilities
│   │   └── tests/               # Unit tests
│   ├── data/                    # Sample SQL files for testing
│   ├── config/                  # Configuration files
│   ├── streamlit_app.py         # Main Streamlit application
│   ├── requirements.txt         # Python dependencies
│   └── README.md               # This file
├── demo/                       # Demo materials
├── presentation/               # Presentation files
└── prompt_screenshots/         # Screenshots for demo
```

## 🎯 Features

### Core Capabilities
- **📊 SQL Lineage Parsing**: Automatically extract table and column dependencies from SQL scripts
- **🔗 Interactive Visualization**: View data flow as interactive graphs with multiple layout options
- **🤖 AI-Powered Explanations**: Ask natural language questions about your data lineage
- **📈 Business Impact Analysis**: Understand downstream effects of data changes

### Technical Features
- **Production-Ready Code**: Built with Pydantic models, proper error handling, and pylint compliance
- **Modern UI**: Clean Streamlit interface with responsive design
- **Multiple Layout Algorithms**: Spring, hierarchical, circular, and force-directed graph layouts
- **Comprehensive Test Data**: Realistic e-commerce, marketing, and financial pipeline examples

## 🧪 Demo Data

The platform includes three comprehensive test datasets:

### 1. E-commerce Pipeline
- **Raw sources**: customers, products, orders, order_items
- **Staging layer**: data cleaning and validation
- **Marts**: customer_summary, product_performance, monthly_sales_summary
- **Reports**: executive_dashboard, customer_retention_cohorts

### 2. Marketing Pipeline  
- **Raw sources**: campaigns, ad_clicks, conversions
- **Analysis**: attribution modeling, user journey analysis
- **Reports**: campaign_performance, channel_effectiveness

### 3. Financial Pipeline
- **Raw sources**: transactions, accounts, budget_allocations
- **Processing**: monthly_financials, budget_vs_actual
- **Reports**: profit_loss_statement, executive_financial_summary

## 🎭 Demo Scenarios

### Quick Test Prompts
1. **Basic Questions**:
   - "Where does customer_summary get its data from?"
   - "What tables depend on raw_orders?"
   - "How does data flow from source to executive dashboard?"

2. **Business Impact**:
   - "If raw_customers has quality issues, what reports are affected?"
   - "What's the lineage behind profit margin calculations?"
   - "Show me all dependencies for marketing ROI analysis"

3. **Technical Analysis**:
   - "Which tables have no upstream dependencies?"
   - "What's the maximum depth of the lineage graph?"
   - "Which intermediate tables are critical junction points?"

### Full Demo Script
1. Upload `sample_ecommerce_pipeline.sql`
2. Analyze the lineage graph visualization
3. Ask: "Explain how customer lifetime value is calculated"
4. Switch to hierarchical layout to see data flow layers
5. Upload additional marketing pipeline for cross-analysis
6. Ask: "What are the main data sources across all pipelines?"

## 🛠️ Development

### Code Quality
```bash
# Run linting
pylint src/lineage_lens/

# Run tests
pytest src/tests/

# Format code
black src/
```

### Architecture Highlights
- **Pydantic Models**: Type-safe data validation and serialization
- **Modular Design**: Separate concerns for parsing, visualization, and AI
- **Error Handling**: Graceful degradation with user-friendly error messages
- **Configuration Management**: Environment-based settings with sensible defaults

## 🎯 Hackathon Goals

**Business Impact**: 
- Reduces data discovery time from hours to minutes
- Enables non-technical users to understand complex data flows
- Improves data governance and impact analysis capabilities

**Technical Excellence**:
- Production-ready code with proper testing and documentation
- Modern Python practices with type hints and validation
- Scalable architecture ready for enterprise deployment

## 🔧 Configuration

Key settings in `src/lineage_lens/utils/config.py`:

```python
# API Configuration
ANTHROPIC_API_KEY=your_key_here

# App Configuration  
APP_TITLE="Lineage Lens"
DEBUG_MODE=false

# Visualization
DEFAULT_LAYOUT="spring"
MAX_NODES_DISPLAY=100
```

## 📊 Sample Outputs

The platform generates:
- **Interactive Graph Visualizations**: Nodes colored by table type (source/intermediate/target)
- **Natural Language Explanations**: Business-friendly descriptions of data flows
- **Summary Statistics**: Table counts, connection metrics, complexity scores
- **Detailed Lineage Tables**: Complete dependency information with SQL queries

## 🚀 Next Steps

For production deployment:
1. Add database connectivity for live metadata extraction
2. Implement caching for large lineage graphs
3. Add user authentication and workspace management
4. Integrate with data catalogs (dbt, Apache Atlas)
5. Add real-time lineage tracking and alerts

## 📈 Business Value

**For Data Engineers**: Faster debugging and impact analysis

**For Business Analysts**: Self-service data discovery without SQL knowledge  

**For Data Governance**: Automated documentation and compliance tracking

**For Leadership**: Clear visibility into data dependencies and risks

---

*Built with ❤️ by the Mindstream Makers Hack-a-Prompt - Transforming complex data lineage into actionable insights*

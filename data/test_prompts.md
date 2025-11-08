# Lineage Lens Test Prompts

## Basic Lineage Questions

### E-commerce Pipeline
1. "Where does the customer_summary table get its data from?"
2. "What tables depend on staging_customers?"
3. "How does data flow from raw_orders to executive_dashboard?"
4. "Which tables are the ultimate source of product information?"
5. "What transformations happen to customer data before it reaches the final reports?"

### Marketing Pipeline  
6. "Trace the data lineage for campaign_performance metrics"
7. "Where does the channel_effectiveness analysis get its data?"
8. "What are all the downstream uses of raw_campaigns data?"
9. "How is user journey analysis connected to conversion data?"
10. "Which tables feed into the attribution analysis?"

### Financial Pipeline
11. "Show me the data flow for profit and loss calculations"
12. "Where does budget_vs_actual get its information from?"
13. "What's the lineage behind executive_financial_summary?"
14. "How do raw transactions flow through the financial reporting pipeline?"
15. "Which tables contribute to department performance metrics?"

## Complex Analysis Questions

### Cross-Pipeline Analysis
16. "What are the main data sources across all three pipelines?"
17. "Which pipelines have the most complex transformation layers?"
18. "Compare the data flow complexity between marketing and financial pipelines"
19. "What tables serve as intermediate staging areas?"
20. "Which final reports have the longest data lineage chains?"

### Business Impact Questions
21. "If raw_customers table has data quality issues, what downstream reports would be affected?"
22. "What would happen to marketing ROI analysis if raw_conversions data is delayed?"
23. "Which executive dashboards depend on real-time transaction data?"
24. "How would missing product information impact sales analysis?"
25. "What financial reports would be impacted if budget allocation data is incorrect?"

## Technical Lineage Questions

### Dependency Analysis
26. "Show me all tables that have no upstream dependencies"
27. "What tables have the most downstream dependencies?"
28. "Which intermediate tables are critical junction points in the data flow?"
29. "What's the maximum depth of the data lineage graph?"
30. "Which tables serve as both source and destination in transformations?"

### Column-Level Questions
31. "How is the customer lifetime value calculated and what source columns does it use?"
32. "Trace the lineage of profit margin calculations"
33. "What source data contributes to campaign ROI metrics?"
34. "How are customer segments derived and from which original fields?"
35. "What transformations are applied to create the value_segment field?"

## Data Quality & Governance Questions

### Impact Analysis
36. "If we change the customer segmentation logic, what downstream tables need updates?"
37. "What reports would be affected by changes to product categorization?"
38. "Which tables should be monitored if campaign data has quality issues?"
39. "What's the blast radius of changes to the staging layer?"
40. "How would schema changes to raw_orders impact the entire pipeline?"

### Compliance & Audit
41. "Show me the complete audit trail for customer revenue calculations"
42. "What source systems contribute to financial regulatory reports?"
43. "How is customer PII data used throughout the marketing pipeline?"
44. "What's the lineage for budget compliance reporting?"
45. "Which tables contain derived vs. source customer information?"

## Performance & Optimization Questions

### Pipeline Efficiency
46. "Which transformations create the most intermediate tables?"
47. "What's the most efficient path from raw data to executive summaries?"
48. "Which staging tables could potentially be eliminated?"
49. "What are the bottleneck tables in each pipeline?"
50. "How can we simplify the data flow while maintaining business logic?"

## Demo Scenarios

### Business User Stories
51. "I'm a new analyst - explain how our customer analytics work"
52. "Walk me through how we calculate marketing effectiveness"
53. "Show me how financial performance is measured in our company"
54. "Explain the relationship between customer behavior and revenue"
55. "How do we track the customer journey from first click to purchase?"

### Technical User Stories  
56. "I need to debug why customer_summary numbers don't match expectations"
57. "Help me understand why the executive dashboard is showing zero revenue"
58. "Trace the data lineage to find where product categories are getting lost"
59. "Show me all the dependencies I need to consider before modifying staging_orders"
60. "What's the impact analysis for adding a new column to raw_campaigns?"

## Edge Cases & Error Scenarios

### Data Quality Issues
61. "What happens when customer_id is null in raw_orders?"
62. "How do we handle missing campaign attribution data?"
63. "What's the impact of duplicate transactions in the financial pipeline?"
64. "How are invalid email addresses handled in customer processing?"
65. "What happens when budget allocation data is missing?"

### Schema Evolution
66. "How would adding a new product attribute affect downstream reports?"
67. "What changes if we split the customer table by geography?"
68. "How would deprecating the raw_order_items table impact analysis?"
69. "What's needed to add real-time streaming data to the batch pipeline?"
70. "How would changing transaction categorization logic propagate?"

## Advanced Analytics Questions

### Machine Learning Integration
71. "How would customer churn prediction models fit into this lineage?"
72. "What data would be needed for product recommendation engines?"
73. "How could we add predictive analytics to marketing attribution?"
74. "What lineage would support financial forecasting models?"
75. "How would real-time personalization integrate with this pipeline?"

## Summary Questions

### Pipeline Overview
76. "Give me a high-level summary of all three data pipelines"
77. "What are the key business metrics these pipelines support?"
78. "How do these pipelines work together to provide business insights?"
79. "What are the main data quality checkpoints in these flows?"
80. "Summarize the most critical data dependencies across all pipelines"

# 📋 AI Agents Framework Backlog

This document tracks planned features, improvements, and known issues for the AI Agents Framework. Items are prioritized by importance and implementation complexity.

## 🔄 In Progress

- **Caching Implementation**: Adding caching for search results and tool responses
  - Memory cache layer (high priority)
  - Disk persistence (medium priority)
  - Cache invalidation strategies (medium priority)

## 🚀 High Priority

1. **Improved Content Extraction**
   - Implement smarter text chunking that preserves sentence integrity
   - Add entity recognition for companies, technologies, and financial terms
   - Create category-specific extractors for different types of financial information
   - Implement relevance scoring system to prioritize useful information
   - Add filters to remove partial sentences and formatting artifacts

2. **Web Fetching Capability**
   - Add ability to fetch and process full website content
   - Implement HTML parsing and content extraction
   - Handle paywalls and access restrictions
   - Support PDF and document processing

3. **LLM Summary Enhancement**
   - Implement improved synthesis step at the end of research
   - Remove redundancy across step results
   - Create more cohesive narrative with proper transitions
   - Fix fragmentary content
   - Normalize writing style

4. **Enhanced Evaluation Metrics**
   - Add benchmark comparisons against expert-created analyses
   - Implement confidence scores for different sections
   - Create domain-specific metrics for different sectors
   - Add source diversity and quality assessment
   - Implement bias detection metric
   - Add financial accuracy metric for numerical claims

## 📊 Medium Priority

5. **Alternative Search Providers**
   - Google Search API integration
   - Bloomberg API for financial data
   - Alpha Vantage for market data
   - SEC Edgar API for regulatory filings
   - NewsAPI for current events
   - Bing Search API as alternative

6. **Query Formulation Optimization**
   - Break complex queries into multiple focused sub-queries
   - Automatically identify key entities and concepts
   - Adjust query terms based on initial search results
   - Add domain-specific terms to improve quality
   - Use structured query templates for research aspects

7. **Caching System Enhancements**
   - Implement distributed caching for multi-agent deployment
   - Add cache analytics and visualization
   - Implement intelligent prefetching for common queries
   - Add cache compression for storage efficiency

8. **Logging and Monitoring Improvements**
   - Enhance structured logging
   - Add performance metrics tracking
   - Implement log rotation and archiving
   - Create dashboard for agent performance monitoring

## 🌟 Low Priority / Future Features

9. **Web UI for Agent Interaction**
   - Create user-friendly web interface
   - Implement real-time progress tracking
   - Add visualization of research process
   - Support history and saved searches

10. **Export Options**
    - PDF export for reports
    - Markdown export for documentation
    - Presentation export (PowerPoint/Google Slides)
    - Data export (CSV/Excel)

11. **Multi-Agent Collaboration**
    - Enable multiple agents to work together
    - Implement task distribution and coordination
    - Add result aggregation and consensus mechanisms
    - Support specialized agent roles

12. **Domain-Specific Agents**
    - Legal research agent
    - Medical research agent
    - Technical/Engineering agent
    - Academic research agent

## 🐛 Known Issues

- Source titles sometimes appear as "None" in search results
- Occasional SSL errors with certain Tavily API calls
- Excessive logging in production mode
- Inconsistent error handling across components
- Memory usage grows with complex research tasks

## 🔄 Completed

- ✅ Initial framework architecture implementation
- ✅ Finance Research Agent implementation
- ✅ Fix for source title extraction
- ✅ Centralized logging configuration
- ✅ Modular tools architecture

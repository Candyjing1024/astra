"""
Generic Services Module for ASTRA Core

TEMPLATE FILE: This module provides generic service templates for your domain-specific implementations.

The services module contains utilities and templates for:
1. AI Search Indexing: Generic indexer for creating and managing search indices
2. Data Processing: Templates for document processing and transformation
3. Azure Integration: Service patterns for Azure cognitive services
4. Custom Services: Extensible patterns for domain-specific services

CUSTOMIZATION:
1. Import and configure the generic indexer for your domain
2. Add your domain-specific service implementations
3. Configure service dependencies and connections
4. Implement custom business logic services

Available Templates:
- ai_search_indexer: Generic Azure AI Search indexer template
"""

from .ai_search_indexer import DomainIndexer, DocumentProcessor

__all__ = [
    'DomainIndexer',
    'DocumentProcessor'
]

# CUSTOMIZE: Add your domain-specific service imports here
# Example:
# from .custom_domain_service import CustomDomainService
# from .data_processor import DataProcessor
# __all__.extend(['CustomDomainService', 'DataProcessor'])
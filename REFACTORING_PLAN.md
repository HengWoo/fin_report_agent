# Server.py Refactoring Plan

## Problem Statement
The `src/mcp_server/server.py` file has grown to 1441 lines, making it difficult to maintain and understand. This document outlines the plan to refactor it into a modular handler architecture.

## Architecture Overview

### ✅ Completed Infrastructure

**Handler Router System:**
- `handler_router.py` (84 lines) - Routes tool calls to appropriate handlers
- `tool_registry.py` (348 lines) - Centralized tool definitions organized by category
- `handlers/base.py` (54 lines) - Base handler class with common formatting and error handling

**Complete Handler Implementations:**
- `handlers/simple_tools_handler.py` (103 lines) - Excel operations (read_excel_region, search_in_excel, get_excel_info, calculate, show_excel_visual)
- `handlers/navigation_handler.py` (127 lines) - LSP-like navigation (find_account, get_financial_overview, get_account_context)
- `handlers/thinking_handler.py` (114 lines) - Metacognition (think_about_financial_data, think_about_analysis_completeness, think_about_assumptions)
- `handlers/memory_handler.py` (110 lines) - Session management (save_analysis_insight, get_session_context, write_memory_note)

**Placeholder Handlers (TODO):**
- `handlers/legacy_analysis_handler.py` - Stub methods created, needs extraction
- `handlers/complex_analysis_handler.py` - Stub methods created, needs extraction

## Implementation Roadmap

### Phase 1: Infrastructure ✅ COMPLETED
- [x] Create handlers/ directory structure
- [x] Implement base handler class with common utilities
- [x] Create handler_router.py for routing tool calls
- [x] Create tool_registry.py for centralized tool definitions
- [x] Implement handlers for simple tools (Excel operations)
- [x] Implement handlers for navigation tools (LSP-like)
- [x] Implement handlers for thinking tools (metacognition)
- [x] Implement handlers for memory tools (session persistence)
- [x] Create placeholder stubs for legacy and complex handlers

### Phase 2: Legacy Handler Extraction 🔄 IN PROGRESS

**Source: server.py lines 514-780**

Need to extract these methods to `handlers/legacy_analysis_handler.py`:

1. **handle_parse_excel** (lines 514-584)
   - Parses Excel files into income statement structure
   - Uses ChineseExcelParser
   - Returns structured financial data

2. **handle_validate_financial_data** (lines 586-626)
   - Validates income statement against industry standards
   - Uses RestaurantFinancialValidator
   - Returns validation results with warnings

3. **handle_calculate_kpis** (lines 628-684)
   - Calculates restaurant KPIs from income statement
   - Uses RestaurantAnalyzer
   - Returns KPI analysis with benchmarks

4. **handle_analyze_trends** (lines 686-732)
   - Analyzes multi-period financial trends
   - Uses RestaurantAnalyzer
   - Returns trend analysis and forecasts

5. **handle_generate_insights** (lines 734-780)
   - Generates strategic business insights
   - Uses BilingualReporter
   - Returns bilingual recommendations

**Dependencies to import:**
```python
from ..parsers.chinese_excel_parser import ChineseExcelParser
from ..validators.restaurant_validator import RestaurantFinancialValidator
from ..analyzers.restaurant_analytics import RestaurantAnalyzer
from ..mcp_server.bilingual_reporter import BilingualReporter
```

### Phase 3: Complex Handler Extraction 🔄 IN PROGRESS

**Source: server.py lines 782-1066**

Need to extract these methods to `handlers/complex_analysis_handler.py`:

1. **handle_comprehensive_analysis** (lines 782-951)
   - End-to-end analysis pipeline
   - Orchestrates parsing → validation → KPI → trends → insights
   - Returns complete bilingual report

2. **handle_adaptive_financial_analysis** (lines 963-1008)
   - Intelligent analysis with business context
   - Adapts to analysis focus (profitability, growth, efficiency, comprehensive)
   - Returns context-aware insights

3. **handle_validate_account_structure** (lines 1010-1066)
   - MANDATORY validation workflow
   - Shows account hierarchy for user confirmation
   - Prevents double-counting errors
   - Returns structured validation results

**Dependencies to import:**
```python
from ..parsers.chinese_excel_parser import ChineseExcelParser
from ..validators.restaurant_validator import RestaurantFinancialValidator
from ..analyzers.restaurant_analytics import RestaurantAnalyzer
from ..mcp_server.bilingual_reporter import BilingualReporter
from ..financial_navigator import financial_navigator
```

### Phase 4: Server.py Integration 📋 TODO

**Current server.py structure:**
```python
class RestaurantFinancialMCPServer:
    def __init__(self):
        # Initialization
        pass

    async def list_tools(self):
        # Returns tool definitions
        pass

    async def call_tool(self, name: str, arguments: dict):
        # Routes to handler methods
        pass
```

**Target refactored structure:**
```python
from .handler_router import HandlerRouter
from .tool_registry import ToolRegistry

class RestaurantFinancialMCPServer:
    def __init__(self):
        self.router = HandlerRouter(server_context={
            'logger': self.logger,
            # other context
        })

    async def list_tools(self):
        return ToolRegistry.get_all_tools()

    async def call_tool(self, name: str, arguments: dict):
        return await self.router.route_tool_call(name, arguments)
```

**Steps:**
1. Replace tool definitions with ToolRegistry.get_all_tools()
2. Initialize HandlerRouter in __init__
3. Replace tool routing logic with router.route_tool_call()
4. Remove all old handler methods (now in handler classes)
5. Keep only server initialization and MCP protocol handling

### Phase 5: Testing & Validation 🧪 TODO

**Test Updates Required:**
1. Update imports to use handlers instead of server methods
2. Test each handler independently
3. Test router dispatching logic
4. Integration tests for complete workflows
5. Verify all 23 tools still work correctly

**Testing Commands:**
```bash
# Run all tests
uv run pytest tests/ -v

# Test specific handlers
uv run pytest tests/test_handlers.py -v

# Integration tests
uv run pytest tests/test_end_to_end.py -v
```

### Phase 6: Documentation 📚 TODO

**Documentation Updates:**
1. Update CLAUDE.md with new architecture
2. Add handler development guide
3. Document how to add new tools
4. Update API documentation
5. Add architecture diagrams

## Benefits of New Architecture

**Code Organization:**
- Server.py reduced from 1441 lines to ~200 lines
- Clear separation of concerns by domain
- Each handler focused on specific functionality
- Easy to locate and modify tool implementations

**Maintainability:**
- Independent handler testing
- Isolated changes don't affect other handlers
- Clear dependencies and imports
- Consistent error handling patterns

**Extensibility:**
- Add new tools by creating new handlers
- Extend existing handlers without touching server.py
- Reusable base handler functionality
- Clear pattern for future development

**Performance:**
- Async handlers for efficient processing
- Lazy loading of handlers
- Minimal coupling between components

## File Size Comparison

**Before Refactoring:**
- server.py: 1441 lines (monolithic)

**After Refactoring:**
- server.py: ~200 lines (core MCP protocol only)
- handler_router.py: 84 lines
- tool_registry.py: 348 lines
- handlers/base.py: 54 lines
- handlers/simple_tools_handler.py: 103 lines
- handlers/navigation_handler.py: 127 lines
- handlers/thinking_handler.py: 114 lines
- handlers/memory_handler.py: 110 lines
- handlers/legacy_analysis_handler.py: ~270 lines (to be extracted)
- handlers/complex_analysis_handler.py: ~285 lines (to be extracted)

**Total Lines:** ~1695 lines (distributed across 11 files)
**Average per file:** ~154 lines (much more manageable)

## Completion Checklist

### Infrastructure ✅
- [x] Handler router implementation
- [x] Tool registry implementation
- [x] Base handler class
- [x] Simple tools handler
- [x] Navigation handler
- [x] Thinking handler
- [x] Memory handler

### Code Extraction 🔄
- [ ] Extract legacy handler methods from server.py
- [ ] Extract complex handler methods from server.py
- [ ] Update server.py to use router
- [ ] Remove old handler code from server.py

### Testing 🧪
- [ ] Unit tests for each handler
- [ ] Integration tests for router
- [ ] End-to-end workflow tests
- [ ] Regression testing for all 23 tools

### Documentation 📚
- [ ] Update CLAUDE.md
- [ ] Add handler development guide
- [ ] Document tool addition process
- [ ] Create architecture diagrams

### Quality Assurance 🔍
- [ ] Code formatting (black)
- [ ] Linting (ruff)
- [ ] Type checking
- [ ] Performance validation

## Next Steps

**Immediate Actions:**
1. Extract legacy handler methods from server.py (lines 514-780)
2. Extract complex handler methods from server.py (lines 782-1066)
3. Refactor server.py to use HandlerRouter
4. Update tool_registry.py to include legacy and complex tools
5. Run full test suite and fix any issues

**Timeline Estimate:**
- Phase 2 (Legacy extraction): 1-2 hours
- Phase 3 (Complex extraction): 1-2 hours
- Phase 4 (Server integration): 1 hour
- Phase 5 (Testing): 1-2 hours
- Phase 6 (Documentation): 1 hour
- **Total: 5-8 hours**

## Notes

- All TODO markers in placeholder handlers indicate exact line numbers in server.py
- Dependencies are clearly documented for each handler
- Error handling patterns established in base.py should be followed
- Async/await patterns must be maintained throughout
- Type hints should be added during extraction
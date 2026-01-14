# Refactoring Roadmap - Financial Inclusion Pipeline

## Identified Redundancies & Fixes

### 1. **CRITICAL: Duplicate Figure Plotting Code** ⚠️
**Location**: `src/run_pipeline.py` lines 175-310  
**Issue**: Each figure plotted twice (PNG + PDF) with nearly identical code  
**Current**: ~150 lines of redundant code  
**Impact**: Maintainability, code duplication (DRY violation)  

**Solution**: Extract figure generation into helper function
```python
def generate_figure(plot_func, data, output_dir, figure_name, figure_config):
    """Generate figure in both PNG and PDF formats"""
    # Save as PNG
    # Save as PDF
```

---

### 2. **Deduplication Logic Duplication**
**Location**: 
- `src/data/deduplicators.py` (core logic)
- `src/audits/dedup_auditor.py` lines 101-180 (audit logic)

**Issue**: `generate_dedup_mapping()` recreates dedup reason detection  
**Fix**: Pass dedup metadata from `deduplicate_full_pipeline()` to auditor

---

### 3. **Unused Code**
**Files to review/remove**:
- `scripts/convert_excel_to_canonical.py` - Never imported or called
- Consider archiving to `docs/legacy/` instead of deleting

**Incomplete Features**:
- VOSviewer integration (fig05) is skipped with warning
- Consider moving to optional module or documenting manual steps

---

### 4. **Data Validation Consolidation**
**Current State**:
- `validators.py` - Schema validation, completeness scores
- `cleaners.py` - Field-specific cleaning
- `auditors.py` - Audit-time validation

**Recommendation**: Document separation of concerns clearly
- Cleaners: Transform raw data
- Validators: Check constraints
- Auditors: Generate reports

---

## Priority Implementation Order

### Phase 1: Quick Wins (Low Risk)
1. ✅ Create figure helper function
2. ✅ Extract figure list to config
3. ✅ Add documentation about unused files

### Phase 2: Refactoring (Medium Risk)
1. Deduplication metadata passing
2. Consolidate validation error handling
3. Create shared plotting utilities

### Phase 3: Cleanup (Low Risk)
1. Archive legacy scripts
2. Add deprecation warnings
3. Update documentation

---

## Testing After Refactoring

- Run full pipeline: `python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures all`
- Compare outputs with current version
- Run test suite: `pytest tests/ -v`

---

## Code Quality Metrics

**Before Refactoring**:
- `run_pipeline.py`: 318 lines (too many concerns)
- Figure code: ~150 lines duplicated
- Cyclomatic complexity: 8+ in main()

**After Refactoring**:
- `run_pipeline.py`: ~200 lines (orchestration only)
- Figure helper module: Shared logic
- Cyclomatic complexity: <5 in main()

---

## Files Marked for Action

```
REVIEW:
├── src/run_pipeline.py (refactor main() function)
├── src/audits/dedup_auditor.py (reduce logic duplication)
├── scripts/convert_excel_to_canonical.py (archive or document)
└── src/figures/__init__.py (add figure registry)

DOCUMENT:
├── docs/REPRODUCIBILITY.md (add refactoring notes)
└── README.md (add architecture section)
```

---

## Implementation Checklist

- [ ] Create `src/figures/registry.py` - Central figure configuration
- [ ] Refactor `run_pipeline.py::main()` to use helper function
- [ ] Add unit tests for figure helper
- [ ] Archive scripts/convert_excel_to_canonical.py → docs/legacy/
- [ ] Update documentation
- [ ] Full pipeline test & validation
- [ ] Git commit with detailed message


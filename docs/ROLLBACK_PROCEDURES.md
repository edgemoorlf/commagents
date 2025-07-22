# Change Management and Rollback Procedures

## Quick Rollback Guide

### Emergency Rollback to Previous Requirements
If the current influencer pipeline approach needs immediate reversal:

```bash
# 1. Checkout the previous requirement version
git checkout req-v2.0-original-content-factory

# 2. Or restore specific files from archive
cp docs/archived_plans/phase3_original_video_production.md temp_restore.md
# Edit CLAUDE.md Phase 3 section with temp_restore.md content

# 3. Remove influencer-specific configuration
rm config/social_media.yaml
rm config/influencer_targets.yaml

# 4. Revert enhanced files to basic versions
git checkout req-v2.0-original-content-factory -- agents/avatar/avatar_personality.py
git checkout req-v2.0-original-content-factory -- core/config_manager.py
```

### Rollback Impact Assessment
Before rolling back, verify impact on:
- [ ] Current development progress (check PROGRESS.md)
- [ ] Configuration files and API integrations
- [ ] Team members working on influencer pipeline features
- [ ] External dependencies and tool integrations

## Change Management Workflow

### For Future Requirement Changes

#### 1. Pre-Change Assessment
```bash
# Create issue branch for requirement change
git checkout -b req-change/description-of-change

# Document current state
git tag -a "pre-change-$(date +%Y%m%d)" -m "State before requirement change"
```

#### 2. Change Documentation Process
1. **Update REQUIREMENTS.md** with new version number and changes
2. **Add entry to CHANGELOG.md** with detailed impact analysis
3. **Archive current plans** to `/docs/archived_plans/` if major changes
4. **Update affected phases** in CLAUDE.md with enhancement/replacement markers
5. **Review and update PROGRESS.md** status and timeline impacts

#### 3. Change Implementation
```bash
# Make changes to documentation and plans
# Commit with descriptive message
git commit -m "Requirements change: [description]

- Updated: [list files changed]
- Impact: [describe scope of change]
- Rollback: Available via tag [tag-name]"

# Tag the change
git tag -a "req-vX.Y-description" -m "Description of requirement change"
```

#### 4. Change Communication
- Update team on requirement changes and impact
- Review timeline adjustments with stakeholders  
- Confirm rollback procedures are understood
- Document any new technical dependencies

## File Roles in Change Management

### CHANGELOG.md
- **Purpose**: Historical record of requirement evolution
- **Update When**: Any significant requirement change
- **Content**: What changed, why, impact analysis, rollback info

### REQUIREMENTS.md  
- **Purpose**: Current active requirements (living document)
- **Update When**: Requirements change or are clarified
- **Content**: Current state, success criteria, technical specs

### PROGRESS.md
- **Purpose**: Implementation progress tracking
- **Update When**: Development milestones reached
- **Content**: What's implemented, what's next, current status

### docs/archived_plans/
- **Purpose**: Historical backup of replaced plans
- **Update When**: Major architectural changes
- **Content**: Complete backup of replaced specifications

## Git Strategy for Change Management

### Tagging Convention
- `req-vX.Y-description`: Major requirement changes
- `phase-X-complete`: Phase completion milestones
- `pre-change-YYYYMMDD`: Pre-change state snapshots

### Branch Strategy
- `main`: Current active requirements and implementation
- `req-change/*`: Requirement change development branches
- `feature/*`: Feature implementation branches

### Commit Message Format
```
[Type]: Brief description

- Changed: [what was modified]
- Added: [what was added]  
- Removed: [what was removed]
- Impact: [effect on other components]
- Rollback: [how to revert if needed]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Rollback Decision Matrix

| Change Scope | Rollback Complexity | Recommended Action |
|--------------|--------------------|--------------------|
| Minor config changes | Low | Direct file revert |
| Single phase enhancement | Medium | Archive + selective revert |
| Multi-phase restructure | High | Full tag rollback + team sync |
| Architecture pivot | Very High | Staged rollback with testing |

## Emergency Procedures

### If System Becomes Unstable After Changes
1. **Immediate**: Rollback to last known stable tag
2. **Assessment**: Review CHANGELOG.md for recent changes
3. **Isolation**: Identify specific change causing issues
4. **Targeted Fix**: Apply minimal fix or selective rollback
5. **Documentation**: Update CHANGELOG.md with issue and resolution

### If Requirements Become Contradictory
1. **Freeze**: Stop current development
2. **Analysis**: Review REQUIREMENTS.md for conflicts
3. **Stakeholder Review**: Clarify priority requirements
4. **Resolution**: Update REQUIREMENTS.md with clarified priorities
5. **Communication**: Update team on requirement resolution

---

*This document should be reviewed and updated with each major requirement change*
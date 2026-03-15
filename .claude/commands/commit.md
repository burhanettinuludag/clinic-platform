# /commit — Smart Conventional Commit

Analyze changes and create a conventional commit with Turkish description.

## Steps

1. Check current state:
```bash
git status
git diff --stat
```

2. If nothing staged, stage relevant changes (ask user which files).

3. Analyze changes and determine commit type:
   - `feat` — New feature
   - `fix` — Bug fix
   - `refactor` — Code restructuring
   - `docs` — Documentation
   - `test` — Test changes
   - `chore` — Maintenance
   - `style` — Formatting/styling
   - `perf` — Performance improvement
   - `security` — Security fix

4. Generate commit message format:
```
<type>(<scope>): <short English summary>

<Detailed Turkish explanation of what changed and why>

Changed files:
- file1.py
- file2.tsx
```

5. Show the message to user for approval BEFORE committing.

6. If approved, commit with the message.

$ARGUMENTS

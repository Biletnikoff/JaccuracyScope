# Phase 1a: C Library Safety

**Branch:** `refactor/1a-c-library-safety`

**Files to modify:**

## Display/Balls/exportme3.c

1. **Line 8**: Rename `main` to `SolveBallistic` (fix non-standard return type)
2. **Line 5**: After `double* sln;` add: `static int sln_valid = 0;`
3. **Lines 30-51**: Before each `SolveAll` call, add:
   ```c
   if (sln != NULL) { free(sln); sln = NULL; sln_valid = 0; }
   ```
4. **Lines 30-51**: Add `else return 0;` fallthrough for unhandled `G` values {2,3,4,5,6,8}
5. **Line 109**: Change `return (GetMOA(sln,Distdesired));` -- add NULL guard
6. **Lines 236-241**: In `free_pointer`, set `sln = NULL; sln_valid = 0;` after `free(sln);`

## Display/Balls/_solve.c

1. **Line 5**: After `malloc`, add:
   ```c
   if (ptr == NULL) return -1;
   ```
2. **Line 8**: Guard velocity:
   ```c
   if (Vi <= 0) return -1;
   ```
3. **Lines 29, 33-34**: Guard against `v == 0`:
   ```c
   if (v < 0.001) break;
   ```

## Display/Balls/_retrieve.c

Add to every `Get*` function (GetRange, GetPath, GetMOA, GetTime, GetWindage,
GetWindageMOA, GetVelocity, GetVx, GetVy):

```c
if (sln == NULL || yardage < 0) return 0;
```

## Display/BallisticThreader4Printer.py (and both Laser variants)

**Lines 37-38**: Update ctypes reference from `main` to `SolveBallistic`:
```python
self.GNUball = self.GNUballCLASS.SolveBallistic
```

## Verification

```bash
cd Display/Balls
gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall -Werror
```

Then run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`

## Hook step (final commit)

In `.github/workflows/ci.yml`, change `-Wall` to `-Wall -Werror`.

Commit: `ci(github): promote C compilation to -Wall -Werror`

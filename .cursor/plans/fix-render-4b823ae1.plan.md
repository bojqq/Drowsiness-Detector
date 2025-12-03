<!-- 4b823ae1-b59e-4b89-96f9-da71fc0c6279 536762b7-b751-4056-9cf0-ad8a69007348 -->
# Remove SciPy to Fix Render Deploy

## Summary

Render fails to build because `scipy==1.11.4` requires a Fortran compiler when installing on Python 3.13. Replace the single SciPy usage (EAR calculations) with a NumPy-based implementation so the backend installs cleanly.

## Steps

1. **Update [`backend/requirements.txt`](backend/requirements.txt)**

- Delete the `scipy==1.11.4` entry so the backend no longer tries to install it.

2. **Update [`backend/api_server.py`](backend/api_server.py)**

- Remove `from scipy.spatial import distance`.
- Add a small `euclidean_distance(point1, point2)` helper using `np.linalg.norm`.
- Update `eye_aspect_ratio_from_landmarks` to call the helper instead of `distance.euclidean`.

3. **Update [`backend/test_properties.py`](backend/test_properties.py)**

- Replace the SciPy import inside `test_ear_calculation_correctness` with the same NumPy helper (defined locally within the test function for clarity).
- Ensure all EAR calculations use the NumPy helper.

4. **Verification**

- Re-run lint/tests locally if available, or at least ensure the files import without SciPy.
- Document in the deploy notes (if needed) that SciPy is no longer required, so Render can rebuild successfully.

### To-dos

- [ ] Remove scipy from backend requirements
- [ ] Replace scipy usage in backend/api_server.py
- [ ] Replace scipy usage in backend/test_properties.py
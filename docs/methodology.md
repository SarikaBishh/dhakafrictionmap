# Methodology

**Question.** If resources were limited, which locations should be investigated first, and what evidence supports that?

**Indicators.** Vehicle count (higher = higher priority), non-motorised share (higher), lane count (lower), signal density (lower). Directions are assumptions about the priority being modelled, not facts about danger. Indicators with different units or observation windows (for example short counts vs annual totals) must not be compared directly.

**Normalisation.** Min-max per indicator to [0,1], flipped when lower = higher priority. If all values are identical every site gets 0.5.

**Score.** `PriorityScore_i = 100 * sum_j(w_j * n_ij)`, weights non-negative and summing to 1. Weights are user-selected assumptions; the defaults (0.35/0.25/0.20/0.20) have no empirical basis.

**Missing data.** Never treated as zero. A missing indicator is dropped for that location, the remaining positive weights are renormalised, and the location is flagged incomplete. If nothing is usable the score is empty and the location is unranked.

**Ranking.** Descending score; ties share the lowest rank (1, 2, 2, 4).

**Sensitivity.** Four weighting scenarios (Default, Equal, Traffic-heavy, Infrastructure-heavy). A location whose rank range is >= 2 is flagged "sensitive". The cut-off of 2 is arbitrary.

**Data quality checks.** Required columns, duplicates, coordinate ranges, dates, numeric/negative/percent values, undeclared blanks, record types; IQR outliers are flagged and kept.

**Can conclude:** how rankings respond to the stated weights. **Cannot conclude:** that a location is objectively dangerous or congested, or that an intervention would work.

**Glossary.** *Min-max normalisation*: rescaling to 0-1. *Sensitivity analysis*: testing whether results survive changes to assumptions. *Synthetic*: invented for testing.

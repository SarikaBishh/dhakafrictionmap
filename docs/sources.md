# Data sources: feasibility notes

Checked on 2026-10-14 by fetching the pages listed. Only what the pages showed is recorded here.

| Source | What was seen | Usable now? |
|---|---|---|
| Mendeley "Bangladeshi Traffic Flow Dataset" v6 (DOI 10.17632/h8bfgtdp2r.6, East West University, published 8 Jan 2025) | Annotated video frames (23,678 images) from four Dhaka locations (Shapla Chattar, Arambag, Bashabo, Abul Hotel), five time intervals on one weekday. The licence was not visible in the fetched text. No coordinates or ready-made counts seen. | Not yet. Counts would have to be derived from annotations, and the licence checked first. |
| RHD Traffic Survey (gis.rhd.gov.bd/trafficsurvey/Report) | A report form: survey year 2021-2026, zone (includes Dhaka), road number, road link, 1st/2nd 24h or 48h, output PDF or Excel. No bulk download or API seen; no licence statement seen (copyright notice: Roads and Highways Department). | Possibly, by manually generating reports. Mostly highway links, so urban coverage is uncertain. Terms unchecked. |
| data.gov.bd transport group | Not fetched. | Unknown |
| OpenStreetMap | Not fetched. Expected to provide road geometry and attributes (ODbL, attribution required), not traffic volumes. | Unknown |

**Decision:** the app runs on a clearly labelled synthetic sample (`data/synthetic/`). No result in this repository is a finding about real Dhaka roads.

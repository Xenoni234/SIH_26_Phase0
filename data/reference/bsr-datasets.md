# BSR / Vasai Road — Reference Facts (from real datasets)

Derived from two real datasets the team provided (India Rail Info, Aug 2026):
- **IRI-Departures-BSR** — 206 mail/express departures from BSR.
- **Vasai Local Train data** — 458 EMU Mumbai locals from BSR (7 PFs).

> These are external, public reference sources for the prototype. Not RTIS. Not official Indian
> Railways data. Used to ground the topology and to seed realistic train numbers/fixtures.

## Station facts
| Field | Value |
| --- | --- |
| Code | **BSR** |
| Name | Vasai Road (local: Bassein Road / वसई रोड) |
| Platforms | **7** (P1–P7) |
| Zone / Division | Western Railway (WR) / Mumbai |
| Category | SG-1 · Junction |
| Track | **Quadruple electric line** (Western corridor) |
| Halting / Originating / Terminating trains | 155 / 7 / 7 (EMU view) |

## Neighboring stations (distance from BSR)
| Code | Station | km | Corridor |
| --- | --- | --- | --- |
| NIG | Naigaon | 4 | Western / Mumbai |
| NSP | Nalla Sopara | 4 | North / Virar |
| JCNR | Juchandra | 5 | Diva |
| VR | Virar | 8 | North / Virar |
| BYR | Bhayandar | 9 | Western / Mumbai |
| KARD | Kaman Road | 11 | Diva |
| MIRA | Mira Road | 12 | Western / Mumbai |
| DIC | Dahisar | 15 | Western / Mumbai |
| VTN | Vaitarna | 17 | North / Virar |
| BVI | Borivali | 18 | Western / Mumbai |

Further down the Western corridor (from the departure data): ADH (Andheri), BA (Bandra),
DDR (Dadar), CCG (Churchgate), DRD (Dahanu Road, up-line beyond Virar/Vaitarna).
Diva corridor terminals seen: DIVA (Diva), PNVL (Panvel).

## Representative train numbers (Vasai-relevant) for RailRadar seeding
- **Diva / Panvel MEMU:** 61003, 61005, 61007 (BSR–Diva); 69168, 69164 (BSR/Dahanu–Panvel).
- **Western locals:** 93002, 93005, 93007, 93004 (BSR–Churchgate/Dahanu fast); 94135, 94136 (AC).
- **Through express/SF:** 12283 (Ernakulam–Nizamuddin Duronto), 12298 (Pune–Ahmedabad Duronto),
  19019 (Bandra–Haridwar), 11049 (Ahmedabad–Kolhapur), 22185 (Ahimsa SF).

## Observed platform usage (BSR)
- Locals cluster on **P1, P3, P4, P5**; through expresses/SF frequently use **P6, P7** (and P1–P5).
- Enough evidence to model **7 platforms** with mixed local/express assignment — encoded in
  `data/topology/vasai.yaml`.

## Notes / caveats
- The local timetable snapshot is community-maintained; treat times as approximate for simulation
  seeding, not as ground truth.
- Distances are station-to-station road/rail approximations from the dataset's "Nearby Stations".

# Wind Coefficient Calculator - IS 875:2015 Part 3

## Overview

This tool calculates wind pressure coefficients for roofs with skylights according to **IS 875:2015 Part 3, Table 22** (Indian Standard Code of Practice for Design Loads - Wind Loads).

## Features

### Calculated Coefficients

1. **Cpe (External Pressure Coefficient)**
   - Zone-wise coefficients for different roof areas
   - Based on roof type (duo-pitch, mono-pitch, flat)
   - Varies with roof slope angle

2. **Cpi (Internal Pressure Coefficient)**
   - Depends on opening conditions:
     - Small openings: Cpi = ±0.2
     - Medium openings: Cpi = ±0.5
     - Large openings: Cpi = -0.5 to +0.7

3. **Combined Coefficients**
   - **Cpe - Cpi**: For uplift/suction forces (critical for fastener design)
   - **Cpe + Cpi**: For pressure forces (structural design)

## Roof Types Supported

1. **Duo-pitch (Gable) Roof**
   - Windward slope zones: A, B, C
   - Leeward slope zones: D, E, F
   - Slope angles: 5° to 45°

2. **Mono-pitch Roof**
   - Zones: A, B, C
   - Slope angles: 5° to 30°

3. **Flat Roof with Skylight**
   - Zones: A, B, C, D
   - Slope: 0° to 5°

## Input Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| Roof Type | Type of roof configuration | Duo-pitch / Mono-pitch / Flat |
| Roof Slope (α) | Pitch angle in degrees | 0° - 45° |
| Building Width (b) | Width in meters | 5 - 100 m |
| Building Length (d) | Length in meters | 5 - 100 m |
| Building Height (h) | Height in meters | 3 - 50 m |
| Skylight Area | Area of skylight opening in m² | 1 - 100 m² |
| Total Roof Area | Complete roof area in m² | 10 - 10,000 m² |
| Opening Condition | Internal pressure classification | Small / Medium / Large |

## Zone Definitions (IS 875-3)

### For Duo-pitch Roofs:

- **Zone A**: Windward edge zone (high suction) - typically b/10 from edge
- **Zone B**: Middle windward zone
- **Zone C**: Central windward zone
- **Zone D**: Leeward edge zone
- **Zone E**: Middle leeward zone
- **Zone F**: Leeward central zone

### For Mono-pitch/Flat Roofs:

- **Zone A**: Windward edge zone (highest suction)
- **Zone B**: Middle zone
- **Zone C**: Central zone
- **Zone D**: Leeward zone (flat roofs only)

## How to Use

1. **Open the Calculator**
   - Open `wind-coefficient-calculator.html` in a web browser
   - No installation or server required

2. **Enter Building Parameters**
   - Select roof type
   - Enter roof slope angle
   - Input building dimensions (width, length, height)
   - Enter skylight area and total roof area
   - Select opening condition

3. **Calculate Coefficients**
   - Click "Calculate Wind Coefficients" button
   - Results will display in organized tables

4. **Interpret Results**
   - Review external coefficients (Cpe) for each zone
   - Check internal coefficients (Cpi) range
   - Use combined coefficients for design:
     - **Cpe - Cpi (max)**: Most critical for uplift/suction
     - **Cpe + Cpi (max)**: Most critical for downward pressure

## Design Recommendations

### Critical Load Cases

1. **Uplift Design (Suction)**
   - Use maximum negative values from **Cpe - Cpi (max)**
   - Critical for:
     - Roof fasteners and anchors
     - Skylight frame connections
     - Roof sheeting/cladding

2. **Downward Pressure**
   - Use positive values from **Cpe + Cpi (max)**
   - Critical for:
     - Structural members (rafters, purlins)
     - Foundation design
     - Overall stability

### Skylight Considerations

- Skylight area > 5% of roof area → Significant internal pressure effects
- Ensure skylight frames can withstand differential pressures
- Consider additional anchoring near skylight edges
- Zone A (edge zones) typically experience highest suction

### Design Wind Pressure Formula

```
p_d = 0.6 × V_z² × C_p  (in N/m²)
```

Where:
- **p_d** = Design wind pressure
- **V_z** = Design wind speed at height z (m/s)
- **C_p** = Pressure coefficient (Cpe ± Cpi)

### Wind Speed Calculation (IS 875-3)

```
V_z = V_b × k_1 × k_2 × k_3
```

Where:
- **V_b** = Basic wind speed (from wind zone map)
- **k_1** = Risk coefficient (terrain, structure height, class)
- **k_2** = Probability factor (design life)
- **k_3** = Topography factor

## Code Compliance

This calculator implements:
- **IS 875 (Part 3):2015** - Code of Practice for Design Loads (Other than Earthquake) for Buildings and Structures
- **Table 22** - Pressure coefficients for roofs with skylights
- Follows all provisions and guidelines from the Indian Standard

## Important Notes

1. **Wind Direction**: Coefficients shown are for wind perpendicular to building face. Analyze multiple wind directions for complete design.

2. **Load Factors**: Apply appropriate partial safety factors as per IS 875-3 and governing design code.

3. **Oblique Winds**: Consider oblique wind angles as per IS 875-3 guidelines for comprehensive analysis.

4. **Local Effects**: Edge zones and corners experience higher local pressures. Use zone-specific coefficients.

5. **Combination**: For structural design, combine wind loads with other loads (dead, live, seismic) as per IS 800 or applicable code.

## File Information

- **File**: `wind-coefficient-calculator.html`
- **Type**: Standalone HTML/JavaScript application
- **Dependencies**: Font Awesome CDN (for icons)
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **No Server Required**: Runs entirely in browser

## Example Calculation

**Given:**
- Duo-pitch roof, slope = 15°
- Building: 20m × 30m × 10m (width × length × height)
- Skylight area: 10 m²
- Total roof area: 600 m²
- Small openings: Cpi = ±0.2

**Results:**
- Zone A (windward edge): Cpe = -1.0
  - Cpe - Cpi = -1.0 - (-0.2) = **-0.8** (suction)
  - Cpe + Cpi = -1.0 + 0.2 = **-0.8** (still suction)

- Zone C (central): Cpe = -0.5
  - Cpe - Cpi = -0.5 - (-0.2) = **-0.3** (suction)
  - Cpe + Cpi = -0.5 + 0.2 = **-0.3** (still suction)

## References

1. **IS 875 (Part 3):2015** - Bureau of Indian Standards
2. **SP 7:2016** - National Building Code of India
3. **IS 800:2007** - General Construction in Steel - Code of Practice

## Version History

- **v1.0** (2025) - Initial release
  - Table 22 implementation for roofs with skylight
  - Support for duo-pitch, mono-pitch, and flat roofs
  - Interactive coefficient calculator
  - Zone-wise Cpe, Cpi, and combined values

## License

This tool is provided for educational and professional use. Ensure all designs are reviewed by qualified structural engineers.

## Support

For questions or issues:
- Refer to IS 875:2015 Part 3 official documentation
- Consult with licensed structural engineers
- Verify calculations independently

---

**Developed for IS 875:2015 Compliance**

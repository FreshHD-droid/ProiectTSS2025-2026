# Diagrama 4 — Control Flow Graph pentru `evaluate_shipment_risk`

> **Cum se folosește:**
> 1. Deschide https://app.diagrams.net/.
> 2. Diagram nou gol → **Extras → Edit Diagram...** (sau pictograma creion).
> 3. Înlocuiește conținutul cu blocul XML de mai jos.
> 4. **OK** → diagrama se randează.
> 5. **File → Export as → PNG** (Transparent Background, Border 10) → salvează ca `Diagrame/cfg_evaluate_shipment_risk.png`.

## Context: ce reprezintă diagrama

Reprezintă fluxul de control al funcției `evaluate_shipment_risk` din `service/risk_evaluator.py`. Fiecare nod este o instrucțiune (sau o decizie). Muchiile sunt etichetate cu `T` / `F` pentru ramurile decizionale, sau neetichetate pentru flux secvențial.

**Punctele de decizie:**

| Eticheta | Locația în cod | Tip |
|---|---|---|
| D1 | `if delay_hours < 0` | simplă |
| D2 | `if not cargo_list` | simplă |
| D_loop | `for c in cargo_list` (implicit: hasNext) | simplă |
| D3 | `if c.is_hazardous` | simplă |
| D4 | `if hazardous_weight > 0 and ratio > 0.7` | **compusă** |
| D5 | `if route.difficulty_factor >= 2.0 and delay_hours > 4` | **compusă (cu `else`)** |
| D6 | `if ratio > 0.5` | simplă |

**Calculul complexității ciclomatice McCabe:**
- n (noduri) = 19 (incluzând nodul virtual EXIT)
- e (muchii) = 25
- p (componente conexe) = 1
- **V(G) = e − n + 2 = 25 − 19 + 2 = 8**
- Verificare: V(G) = #decizii + 1 = 7 + 1 = **8** ✓

## Cod mxGraph (draw.io)

```xml
<mxfile host="app.diagrams.net" modified="2026-04-26T12:00:00.000Z" agent="claude" version="24.0.0">
  <diagram name="CFG_evaluate_shipment_risk" id="diag4">
    <mxGraphModel dx="1400" dy="1600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="900" pageHeight="1700" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="title" value="&lt;b&gt;CFG — evaluate_shipment_risk&lt;/b&gt;&#xa;V(G) = e − n + 2 = 25 − 19 + 2 = 8" style="text;html=1;align=center;verticalAlign=middle;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="280" y="20" width="400" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="n_start" value="START" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="380" y="90" width="120" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_d1" value="&lt;b&gt;D1&lt;/b&gt;&#xa;delay_hours &lt; 0 ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="360" y="170" width="160" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="n_raise_delay" value="raise NegativeDelayError" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="600" y="190" width="200" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_d2" value="&lt;b&gt;D2&lt;/b&gt;&#xa;not cargo_list ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="360" y="290" width="160" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="n_raise_empty" value="raise EmptyCargoListError" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="600" y="310" width="220" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_init" value="total_weight = 0&#xa;hazardous_weight = 0" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="370" y="410" width="200" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="n_loop" value="&lt;b&gt;D_loop&lt;/b&gt;&#xa;c in cargo_list ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="370" y="490" width="180" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="n_body1" value="total_weight += c.weight" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="510" width="200" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_d3" value="&lt;b&gt;D3&lt;/b&gt;&#xa;c.is_hazardous ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="120" y="580" width="160" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="n_haz_assign" value="hazardous_weight += c.weight" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="80" y="700" width="240" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_ratio" value="ratio = total_weight / train.max_capacity" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="640" y="500" width="240" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="n_d4" value="&lt;b&gt;D4 (compusă)&lt;/b&gt;&#xa;hazardous_weight &gt; 0&#xa;AND ratio &gt; 0.7 ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="640" y="580" width="240" height="100" as="geometry"/>
        </mxCell>

        <mxCell id="n_return_high1" value="return &quot;HIGH&quot;&#xa;(rule 1)" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="700" y="710" width="160" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="n_d5" value="&lt;b&gt;D5 (compusă, cu else)&lt;/b&gt;&#xa;difficulty_factor &gt;= 2.0&#xa;AND delay_hours &gt; 4 ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="370" y="800" width="240" height="100" as="geometry"/>
        </mxCell>

        <mxCell id="n_high2" value="risk = &quot;HIGH&quot;&#xa;(rule 2)" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="660" y="820" width="160" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="n_d6" value="&lt;b&gt;D6&lt;/b&gt;&#xa;ratio &gt; 0.5 ?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="160" y="950" width="160" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="n_medium" value="risk = &quot;MEDIUM&quot;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="20" y="1080" width="160" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_low" value="risk = &quot;LOW&quot;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="300" y="1080" width="160" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="n_return_risk" value="return risk" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="380" y="1180" width="160" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="n_exit" value="EXIT" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="400" y="1280" width="120" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="e_start_d1" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="n_start" target="n_d1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d1_T" value="T" style="endArrow=classic;html=1;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d1" target="n_raise_delay">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d1_F" value="F" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d1" target="n_d2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d2_T" value="T" style="endArrow=classic;html=1;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d2" target="n_raise_empty">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d2_F" value="F" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d2" target="n_init">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_init_loop" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="n_init" target="n_loop">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_loop_T" value="T (mai are)" style="endArrow=classic;html=1;exitX=0;exitY=0.5;entryX=1;entryY=0.5;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_loop" target="n_body1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_body1_d3" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="n_body1" target="n_d3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d3_T" value="T" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d3" target="n_haz_assign">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d3_F_back" value="F (back)" style="endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.7;fontSize=11;fontStyle=1;dashed=1;" edge="1" parent="1" source="n_d3" target="n_loop">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_haz_back" value="back" style="endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=1;fontSize=11;fontStyle=1;dashed=1;" edge="1" parent="1" source="n_haz_assign" target="n_loop">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_loop_F" value="F (gata)" style="endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_loop" target="n_ratio">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_ratio_d4" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="n_ratio" target="n_d4">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d4_T" value="T" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d4" target="n_return_high1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d4_F" value="F" style="endArrow=classic;html=1;exitX=0;exitY=0.5;entryX=1;entryY=0.5;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d4" target="n_d5">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d5_T" value="T" style="endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d5" target="n_high2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d5_F" value="F (else)" style="endArrow=classic;html=1;exitX=0;exitY=0.5;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d5" target="n_d6">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d6_T" value="T" style="endArrow=classic;html=1;exitX=0;exitY=0.5;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d6" target="n_medium">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_d6_F" value="F" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;fontSize=11;fontStyle=1;" edge="1" parent="1" source="n_d6" target="n_low">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_high2_ret" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=1;entryY=0.5;" edge="1" parent="1" source="n_high2" target="n_return_risk">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_med_ret" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0;entryY=0.5;" edge="1" parent="1" source="n_medium" target="n_return_risk">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_low_ret" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="n_low" target="n_return_risk">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_ret_exit" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="n_return_risk" target="n_exit">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_raise_delay_exit" style="endArrow=classic;html=1;exitX=1;exitY=0.5;dashed=1;strokeColor=#b85450;" edge="1" parent="1" source="n_raise_delay" target="n_exit">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="850" y="210"/>
              <mxPoint x="850" y="1300"/>
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e_raise_empty_exit" style="endArrow=classic;html=1;exitX=1;exitY=0.5;dashed=1;strokeColor=#b85450;" edge="1" parent="1" source="n_raise_empty" target="n_exit">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="870" y="330"/>
              <mxPoint x="870" y="1300"/>
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e_return_high1_exit" style="endArrow=classic;html=1;exitX=1;exitY=0.5;dashed=1;" edge="1" parent="1" source="n_return_high1" target="n_exit">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="890" y="735"/>
              <mxPoint x="890" y="1300"/>
            </Array>
          </mxGeometry>
        </mxCell>

        <mxCell id="legend" value="&lt;b&gt;Legenda:&lt;/b&gt;&#xa;◇ albastru: START / EXIT (intrare/ieșire virtuale)&#xa;◇ galben: nod de decizie (D1-D6, D_loop)&#xa;▭ violet: bloc de instrucțiuni (proces)&#xa;▭ rosu: terminal cu excepție (raise)&#xa;◯ rosu: ieșire cu return &quot;HIGH&quot; (rule 1)&#xa;Linii continue: flux normal&#xa;Linii intrerupte: back-edge (loop) / sărituri către EXIT" style="rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;fillColor=#ffffff;strokeColor=#666666;fontSize=10;spacingLeft=8;spacingTop=6;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="20" y="1180" width="320" height="140" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Independent paths (set de bază)

V(G) = 8 → 8 căi liniar independente. Fiecare cale corespunde unei combinații unice de decizii:

| # | Cale | Decizii | Rezultat |
|---|------|---------|----------|
| P1 | START → D1=T → raise NegDelayErr → EXIT | D1=T | excepție |
| P2 | START → D1=F → D2=T → raise EmptyCargo → EXIT | D1=F, D2=T | excepție |
| P3 | ...→ D2=F → init → loop=1iter no-haz → D4=F → D5=T → HIGH → return | D5=T | "HIGH" (rule 2) |
| P4 | ...→ D5=F → D6=T → MEDIUM → return | D5=F, D6=T | "MEDIUM" |
| P5 | ...→ D5=F → D6=F → LOW → return | D5=F, D6=F | "LOW" |
| P6 | ...→ loop=1iter haz → D4=T → return HIGH | D3=T, D4=T | "HIGH" (rule 1) |
| P7 | ...→ loop=1iter haz → D4=F → D5=F → D6=F → LOW | D3=T, D4=F, D6=F | "LOW" |
| P8 | ...→ loop=2+ iter (mix) → ... → return | D_loop iterează 2+ | (dependent de date) |

Fiecare cale are un test corespondent în `tests/test_risk_evaluator_whitebox.py`.

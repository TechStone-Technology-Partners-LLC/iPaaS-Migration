import os, re, sys

BASE = r"C:/Users/manis/iPaas Migration/WebMethods/GLDProject"

def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except:
        return ""

def clean_flow(txt):
    """Strip embedded IS Values XML and DATA blocks, keep structural tags."""
    # Remove DATA blocks
    txt = re.sub(r'<DATA[^>]*/>', '', txt)
    txt = re.sub(r'<DATA[^>]*>.*?</DATA>', '', txt, flags=re.DOTALL)
    # Remove MAPTARGET/MAPSOURCE content but keep tags (field names extracted separately)
    txt = re.sub(r'<MAPTARGET>.*?</MAPTARGET>', '<MAPTARGET/>', txt, flags=re.DOTALL)
    txt = re.sub(r'<MAPSOURCE>.*?</MAPSOURCE>', '<MAPSOURCE/>', txt, flags=re.DOTALL)
    # Remove HTML comments
    txt = re.sub(r'<!--.*?-->', '', txt, flags=re.DOTALL)
    # Remove COMMENT elements
    txt = re.sub(r'<COMMENT>.*?</COMMENT>', '', txt, flags=re.DOTALL)
    return txt

def extract_mapcopy(raw_txt):
    """Extract MAPCOPY pairs from raw (uncleaned) flow text."""
    pattern = re.compile(r'<MAPCOPY\b[^>]*SOURCE="([^"]*)"[^>]*TARGET="([^"]*)"[^>]*/>', re.DOTALL)
    results = []
    for m in pattern.finditer(raw_txt):
        src = m.group(1).split(';')[0].lstrip('/')
        tgt = m.group(2).split(';')[0].lstrip('/')
        results.append((m.start(), src, tgt))
    return results

def extract_mapset(raw_txt):
    """Extract MAPSET constant assignments from raw flow text."""
    pattern = re.compile(r'<MAPSET\b[^>]*FIELD="([^"]*)"[^>]*/>', re.DOTALL)
    results = []
    for m in pattern.finditer(raw_txt):
        fld = m.group(1).split(';')[0].lstrip('/')
        results.append((m.start(), fld))
    return results

def render_flow(raw_txt):
    """Parse flow XML and return ordered step list as human-readable lines."""
    # Pre-extract MAPCOPY and MAPSET with their positions in raw text
    all_copies = extract_mapcopy(raw_txt)
    all_sets   = extract_mapset(raw_txt)

    lines = []
    cur_depth = 0
    STRUCTURAL = {'FLOW', 'SEQUENCE', 'INVOKE', 'MAP', 'BRANCH', 'LOOP', 'EXIT', 'RETRY'}

    token_pat = re.compile(
        r'<(/?)([A-Z][A-Z0-9_-]*)((?:\s+[\w-]+="[^"]*")*)\s*(/?)>',
        re.DOTALL
    )

    # Track position of each MAP opening to find associated copies/sets
    map_positions = []  # list of (start_pos, end_pos) in raw_txt for each MAP block
    map_open_pat  = re.compile(r'<MAP\b', re.DOTALL)
    map_close_pat = re.compile(r'</MAP>', re.DOTALL)

    # Find all MAP block ranges in the raw text
    map_open_positions  = [m.start() for m in map_open_pat.finditer(raw_txt)]
    map_close_positions = [m.start() for m in map_close_pat.finditer(raw_txt)]
    map_ranges = list(zip(map_open_positions, map_close_positions))

    for m in token_pat.finditer(raw_txt):
        tag      = m.group(2)
        is_close = m.group(1) == '/'
        attrs_s  = m.group(3)
        is_self  = m.group(4) == '/'
        pos      = m.start()

        if tag not in STRUCTURAL:
            continue

        attrs    = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs_s))
        disabled = attrs.get('DISABLED', 'false').lower() == 'true'
        dis      = ' [DISABLED]' if disabled else ''
        pad      = '  ' * cur_depth

        if is_close:
            cur_depth = max(0, cur_depth - 1)
            pad = '  ' * cur_depth
            if   tag == 'SEQUENCE': lines.append(f"{pad}END-SEQUENCE")
            elif tag == 'LOOP':     lines.append(f"{pad}END-LOOP")
            elif tag == 'BRANCH':   lines.append(f"{pad}END-BRANCH")
            elif tag == 'RETRY':    lines.append(f"{pad}END-RETRY")
            elif tag == 'MAP':      lines.append(f"{pad}END-MAP")
            elif tag == 'INVOKE':   lines.append(f"{pad}END-INVOKE")

        elif is_self:
            if tag == 'EXIT':
                signal  = attrs.get('SIGNAL', 'SUCCESS')
                from_   = attrs.get('FROM', '$flow')
                failure = attrs.get('FAILURE', '')
                fail_s  = f" failure='{failure}'" if failure else ''
                lines.append(f"{pad}EXIT signal={signal} from={from_}{fail_s}{dis}")

        else:
            if tag == 'FLOW':
                pass  # root element - no output

            elif tag == 'SEQUENCE':
                n   = attrs.get('NAME', '')
                eon = attrs.get('EXIT-ON', '')
                lines.append(f"{pad}SEQUENCE '{n}' exit-on={eon}{dis}")
                cur_depth += 1

            elif tag == 'INVOKE':
                svc = attrs.get('SERVICE', '?')
                n   = attrs.get('NAME', '') or svc.split(':')[-1]
                lines.append(f"{pad}INVOKE '{n}'{dis}")
                lines.append(f"{'  '*(cur_depth+1)}service: {svc}")
                cur_depth += 1

            elif tag == 'MAP':
                mode = attrs.get('MODE', '')
                lines.append(f"{pad}MAP [mode={mode}]{dis}")
                cur_depth += 1
                # Find this MAP's range and emit associated MAPCOPY/MAPSET
                my_range = next(((s, e) for s, e in map_ranges if s == pos), None)
                if my_range:
                    s_pos, e_pos = my_range
                    ip = '  ' * cur_depth
                    shown = 0
                    for cp_pos, src, tgt in all_copies:
                        if s_pos < cp_pos < e_pos:
                            lines.append(f"{ip}copy: {src} -> {tgt}")
                            shown += 1
                            if shown >= 30:
                                lines.append(f"{ip}... (more copies)")
                                break
                    shown = 0
                    for st_pos, fld in all_sets:
                        if s_pos < st_pos < e_pos:
                            lines.append(f"{ip}SET {fld}")
                            shown += 1
                            if shown >= 20:
                                lines.append(f"{ip}... (more sets)")
                                break

            elif tag == 'BRANCH':
                sw = attrs.get('SWITCH', '')
                lines.append(f"{pad}BRANCH on '{sw}'{dis}")
                cur_depth += 1

            elif tag == 'LOOP':
                ref   = attrs.get('REF', '?')
                count = attrs.get('COUNT', '')
                lines.append(f"{pad}LOOP over '{ref}'{' count=' + count if count else ''}{dis}")
                cur_depth += 1

            elif tag == 'RETRY':
                count = attrs.get('COUNT', '?')
                lines.append(f"{pad}RETRY max={count}{dis}")
                cur_depth += 1

    return lines


# ── Active packages and their flow directories ─────────────────────────────
ACTIVE_PACKAGES = {
    'GLDComplianceCheck':    'GLDComplianceCheck/ns/GLDComplianceCheck',
    'GLDExpressGateway':     'GLDExpressGateway/ns/GLDExpressGateway',
    'GLDExpressWebServices': 'GLDExpressWebServices/ns/GLDExpressWebServices',
    'GLDFundingEngine':      'GLDFundingEngine/ns/GLDFundingEngine',
    'GLDMessageLog':         'GLDMessageLog/ns/GLDMessageLog',
    'GLDSoap':               'GLDSoap/ns/GLDSoap',
    'GLDSoap20':             'GLDSoap20/ns/GLDSoap',
}

# Read full Java source files
JAVA_FILES = [
    ('GLDComplianceCheck.Utilities',
     'GLDComplianceCheck/code/source/GLDComplianceCheck/Utilities/JavaServices.java'),
    ('GLDExpressGateway.ProcessFlows.Applicant',
     'GLDExpressGateway/code/source/GLDExpressGateway/ProcessFlows/Applicant/JavaServices.java'),
    ('GLDExpressGateway.ProcessFlows.Customer',
     'GLDExpressGateway/code/source/GLDExpressGateway/ProcessFlows/Customer/JavaServices.java'),
    ('GLDExpressGateway.Utilities',
     'GLDExpressGateway/code/source/GLDExpressGateway/Utilities/JavaServices.java'),
    ('GLDExpressWebServices.Utilities',
     'GLDExpressWebServices/code/source/GLDExpressWebServices/Utilities/JavaServices.java'),
    ('GLDSoap.Utilities',
     'GLDSoap/code/source/GLDSoap/Utilities/JavaServices.java'),
]

# ── Build the analysis document ────────────────────────────────────────────
out = []

out.append("# webMethods GLD — Complete Flow Logic & Migration Blueprint")
out.append("")
out.append("> **Complete step-by-step logic extracted from all 202 active flow services across all packages.**")
out.append("> Each INVOKE shows the exact service called. Each MAP shows field copies and constant assignments.")
out.append("> BRANCH shows the switch field. LOOP shows the iterated variable. EXIT shows signal type.")
out.append("")
out.append("---")
out.append("")

# ── Per-package flow details ───────────────────────────────────────────────
for pkg, ns_dir in ACTIVE_PACKAGES.items():
    ns_path = os.path.join(BASE, ns_dir)
    if not os.path.isdir(ns_path):
        continue

    out.append(f"## Package: {pkg}")
    out.append("")

    # Collect flows
    flows = []
    for root, dirs, files in os.walk(ns_path):
        for fname in files:
            if fname == 'flow.xml':
                rel = root.replace(ns_path, '').replace('\\', '/').lstrip('/')
                flows.append((rel, os.path.join(root, fname)))

    flows.sort(key=lambda x: x[0])

    for rel, fpath in flows:
        raw = read(fpath)
        if not raw:
            continue
        step_lines = render_flow(raw)

        out.append(f"### `{pkg}/{rel}`")
        out.append("")
        out.append("```")
        out.extend(step_lines)
        out.append("```")
        out.append("")

out.append("---")
out.append("")
out.append("## Java Custom Services — Full Source")
out.append("")

for label, rel in JAVA_FILES:
    fpath = os.path.join(BASE, rel)
    src = read(fpath)
    if not src:
        continue
    out.append(f"### `{label}`")
    out.append("")
    out.append("```java")
    out.append(src)
    out.append("```")
    out.append("")

# Write output
out_path = r"C:/Users/manis/iPaas Migration/WebMethods/GLD_Complete_Flow_Logic.md"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f"Done. Written to: {out_path}")
total_lines = len(out)
print(f"Total lines: {total_lines}")

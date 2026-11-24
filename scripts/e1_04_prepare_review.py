"""ENG-E1-04: package the existing v2 reviewer export locally; no human labels."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse
import json
import subprocess
import sys
import tempfile
import uuid
import zipfile

PUBLIC = ('packet.json', 'BLANK.json', 'REVIEWER_OFFLINE.html', 'REVIEWER_GUIDE_PT_EN.md')
SCHEMA = 'rightware-e1c-independent-review-v2'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_packet(packet, blank, slot):
    require(packet.get('schema_version') == SCHEMA and blank.get('schema_version') == SCHEMA, 'Not v2')
    require(packet.get('review_slot') == slot and packet.get('status') == 'REVIEWER_OPAQUE_TRAIN_DEV_NO_GOLD', 'Wrong slot/status')
    require(blank.get('review_status') == 'NOT_SUBMITTED' and blank.get('reviewer_pseudonym') == '' and blank.get('independence_attested') is False and blank.get('provisional_gold_not_consulted') is False, 'Not blank')
    require(len(packet['documents']) == 42 and len(packet['queries']) == 24 and len(blank['judgments']) == 24, 'Unexpected counts')
    require(all(d['split'] in ('train', 'dev') and d['source_id'].startswith('DOC-') for d in packet['documents']), 'Unexpected document')
    require(all(q['split'] in ('train', 'dev') and q['query_id'].startswith('QUE-') for q in packet['queries']), 'Unexpected query')
    require(all(j['query_class'] == 'UNSET' and j['conflict_claims'] == [] and all(r['grade'] is None and not r['justification'] and not r['evidence_quote'] for r in j['ratings']) for j in blank['judgments']), 'Nonblank judgments')
    require(sum(len(j['ratings']) for j in blank['judgments']) == 560, 'Unexpected rating count')
    digest = sha256(json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
    require(blank['packet_sha256'] == digest, 'Packet hash mismatch')
    require(blank['dataset_id'] == packet['dataset_id'] and blank['data_sha256'] == packet['data_sha256'], 'Dataset mismatch')


def archive(slot_dir, target, assets, slot):
    """Only explicit allowlisted files; never walk the custody directory."""
    require(all((slot_dir / n).is_file() and not (slot_dir / n).is_symlink() for n in PUBLIC[:2]), 'Missing or symlinked review files')
    p = json.loads((slot_dir / 'packet.json').read_text(encoding='utf-8'))
    b = json.loads((slot_dir / 'BLANK.json').read_text(encoding='utf-8'))
    verify_packet(p, b, slot)
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for n in PUBLIC:
            z.write((slot_dir if n in PUBLIC[:2] else assets) / n, n)
    with zipfile.ZipFile(target) as z:
        require(tuple(z.namelist()) == PUBLIC and z.testzip() is None, 'Archive integrity failed')
    return sha256(target.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default='.', help='Local SIC Git checkout')
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    assets = repo / 'docs/research/e1_04'
    require((repo / 'scripts/e1_03_review.py').is_file(), 'Select SIC repository root')
    require(all((assets / n).is_file() for n in PUBLIC[2:]), 'Missing offline reviewer assets')
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=repo, text=True).strip()
    require(branch == 'develop', 'Use develop; no automatic branch switch')
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True).strip(), 'Working tree must be clean')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    require(subprocess.run(['git', 'check-ignore', '-q', '.runtime/e1_04_probe'], cwd=repo).returncode == 0, '.runtime must be ignored')
    private = repo / '.runtime'
    require(not private.is_symlink(), 'Refusing symlinked .runtime')
    private.mkdir(mode=0o700, exist_ok=True)
    folder = private / ('e1_04_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:12])
    # Existing reviewed exporter generates opaque aliases; no network use here.
    subprocess.run([sys.executable, 'scripts/e1_03_review.py', '--mode', 'self-check'], cwd=repo, check=True)
    subprocess.run([sys.executable, 'scripts/e1_03_review.py', '--mode', 'export', '--output-dir', str(folder.relative_to(repo))], cwd=repo, check=True)
    require((folder / 'CUSTODY_ONLY/PRIVATE_ALIAS_MAP.json').is_file(), 'Missing private mapping')
    hashes = {slot: archive(folder / ('reviewer_' + slot), folder / ('REVIEWER_' + slot + '.zip'), assets, slot) for slot in ('A', 'B')}
    receipt = {'status': 'PACKAGED_NOT_DISTRIBUTED', 'head': head, 'archive_sha256': hashes, 'human_submissions': 0, 'science_gate': 'REVIEW_REQUIRED'}
    with (folder / 'CUSTODY_ONLY/PACKAGING_RECEIPT.json').open('x', encoding='utf-8') as out:
        json.dump(receipt, out, indent=2)
    print('PACKAGING_PASS', folder)
    print('Before sharing: local browser smoke and approved private custody.')
    print('Share only the separate REVIEWER_A.zip / REVIEWER_B.zip. Never share CUSTODY_ONLY.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Offline data publisher. Never packaged in the app; no app sources are exported."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

LIMIT = 12_000_000
REFERENCE = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)


def build(converter, output):
    sources = []
    for name, title in [('easylist', 'EasyList'), ('easyprivacy', 'EasyPrivacy')]:
        data = subprocess.run([
            'curl', '--fail', '--silent', '--show-error', '--location',
            '--proto', '=https', '--proto-redir', '=https', '--max-time', '90',
            '--max-filesize', str(LIMIT), '--retry', '2',
            f'https://easylist.to/easylist/{name}.txt'
        ], check=True, capture_output=True, timeout=300).stdout
        text = data.decode('utf-8')
        if len(data) >= LIMIT or not text.startswith('[Adblock Plus') or f'! Title: {title}' not in text:
            raise ValueError('Invalid filter source')
        sources.append(text)
    with tempfile.TemporaryDirectory() as temporary:
        combined = Path(temporary) / 'combined.txt'
        combined.write_text('\n'.join(sources))
        result = subprocess.run([str(converter), 'convert', '--safari-version', '26',
                                 '--advanced-blocking', 'false', '--input-path', str(combined)],
                                check=True, capture_output=True, text=True, timeout=300)
        conversion = json.loads(result.stdout)
    rules = json.loads(conversion['safariRulesJSON'])
    count = len(rules)
    if not 10_000 < count <= 150_000 or count != conversion['safariRulesCount'] or conversion['discardedSafariRules'] != 0:
        raise ValueError('Incomplete conversion')
    if conversion['errorsCount'] > max(1000, conversion['sourceRulesCount'] * 0.01):
        raise ValueError('Unexpected increase in unsupported filters')
    for rule in rules:
        if rule['action']['type'] not in ['block', 'css-display-none', 'ignore-previous-rules'] or not rule['trigger']['url-filter']:
            raise ValueError('Unexpected native rule')
    rule_json = json.dumps(rules, separators=(',', ':'), ensure_ascii=False)
    now = datetime.datetime.now(datetime.timezone.utc)
    feed = {'schemaVersion': 1,
            'snapshot': {'json': rule_json, 'date': (now - REFERENCE).total_seconds(), 'count': count},
            'sha256': hashlib.sha256(rule_json.encode()).hexdigest()}
    encoded = json.dumps(feed, separators=(',', ':'), ensure_ascii=False).encode()
    if len(encoded) > 48_000_000:
        raise ValueError('Feed too large')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'latest.json').write_bytes(encoded)
    (output / 'provenance.json').write_text(json.dumps({
        'generatedAt': now.isoformat(), 'converter': 'SafariConverterLib 4.3.1',
        'converterCommit': '1cfdcaf042880a5e0027a8fc6f7ebf9ee667acc9',
        'safariVersion': 26, 'advancedBlocking': False, 'count': count,
        'unsupportedRules': conversion['errorsCount'], 'discardedRules': 0,
        'sourceSHA256': [hashlib.sha256(source.encode()).hexdigest() for source in sources],
        'sources': ['https://easylist.to/easylist/easylist.txt', 'https://easylist.to/easylist/easyprivacy.txt'],
        'license': 'CC-BY-SA-3.0'
    }, indent=2) + '\n')
    print(f'Validated {count} native rules; {conversion["errorsCount"]} unsupported source rules.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--converter', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.converter.resolve(), args.output)

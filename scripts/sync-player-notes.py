"""Generate website player notes from reviewed release records. Published signed manifests are never edited."""
from pathlib import Path
import argparse,datetime,json

def main():
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',required=True)
    parser.add_argument('--output',type=Path,default=root.parent/'HLMC-Reborn-Website/src/lib/release-notes.json')
    args=parser.parse_args();records={}
    for path in sorted((root/'release-notes').glob('*.json')):
        value=json.loads(path.read_text(encoding='utf8'));version=value['version']
        assert path.stem==version
        datetime.date.fromisoformat(value['date'])
        for language in ['en','ru','lv']:
            notes=value['locales'][language]
            assert isinstance(notes['changes'],list) and 1<=len(notes['changes'])<=8
            for text in [notes['summary'],notes['teaser'],*notes['changes']]:
                assert isinstance(text,str) and text.strip() and '\u2014' not in text
                assert 'pjampjam' not in text.lower() and 'pjamtest' not in text.lower(), 'Operational account notes belong in admin records'
        records[version]=value
    assert args.version in records
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'latest':args.version,'releases':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Player notes generated for '+args.version)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Install advanced games without changing any of the 194 embedded MP3 bytes."""
from pathlib import Path
import re,json,subprocess
root=Path(__file__).resolve().parent.parent
page=root/'index.html'
s=page.read_text(encoding='utf-8')
source=(root/'scripts/advanced_games.js').read_text(encoding='utf-8')
if '/* Starwhim Island: advanced puzzles, compatible' in s:
    beginning=s.rfind('<script>',0,s.index('/* Starwhim Island: advanced puzzles, compatible'))
    ending=s.find('</script>',s.index('/* Starwhim Island: advanced puzzles, compatible'))+len('</script>')
    assert beginning>=0 and ending>beginning
    s=s[:beginning]+s[ending:]
    print('Replacing previous advanced games script')
assert 'S.MINIGAMES=[' in s and 'S.minigames=M;' in s
assert 'S.audio.speak=speak;' in s
assert s.count('</body>')==1
assert 'window.StarwhimAdvancedGames={version:1' in source
subprocess.run(['node','--check',str(root/'scripts/advanced_games.js')],check=True)
new=s.replace('</body>','<script>\n'+source.replace('</script>','<\\/script>')+'\n</script>\n</body>',1)
assert len(new)>len(s) and len(new)<len(s)+15000
assert new.count('</body>')==1
pack=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',new,re.S)
assert pack and len(json.loads(pack.group(1))['audio'])>=194
page.write_text(new,encoding='utf-8')
print('Advanced games installed:', ['starmaze','starsudoku','elfcode'])

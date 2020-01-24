from pathlib import Path
import tempfile

PATH = Path(__file__).parent
print(str(PATH))
print(tempfile.mkstemp(suffix='.db',prefix='test_db'))

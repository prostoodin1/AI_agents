from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_agents.file_agent import main

main()

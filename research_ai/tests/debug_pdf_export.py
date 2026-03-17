import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

from backend.proposal.proposal_writer import ProposalWriter

def test_export():
    writer = ProposalWriter()
    output_path = os.path.join(project_root, "db", "reports", "test_debug.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    writer.export_pdf("# Debug\nHello World", output_path)
    print(f"Exported to {output_path}")

if __name__ == "__main__":
    try:
        test_export()
    except Exception as e:
        import traceback
        traceback.print_exc()

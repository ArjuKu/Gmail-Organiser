import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [scan_senders|apply_senders|streamlit]")
        print("\nRecommended: Use Streamlit for better experience:")
        print("  streamlit run src/app.py")
        return

    command = sys.argv[1]

    if command == "scan_senders":
        from src.scan_senders import run_scan_senders
        run_scan_senders()
    elif command == "apply_senders":
        from src.apply_senders import run_apply_senders
        run_apply_senders()
    elif command == "streamlit":
        os.system("streamlit run src/app.py")
    else:
        print(f"Unknown command: {command}")
        print("\nUse 'streamlit' to launch the web interface!")

if __name__ == "__main__":
    main()

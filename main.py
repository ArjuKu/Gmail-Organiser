import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [scan|apply|run]")
        print("\nRecommended: Use 'run' to launch the web interface")
        return

    command = sys.argv[1]

    if command == "scan":
        from core.scan_senders import run_scan_senders
        run_scan_senders()
    elif command == "apply":
        from core.apply_senders import run_apply_senders
        run_apply_senders()
    elif command == "run":
        os.system("streamlit run app/app.py")
    else:
        print(f"Unknown command: {command}")
        print("\nUse 'run' to launch the web interface!")

if __name__ == "__main__":
    main()

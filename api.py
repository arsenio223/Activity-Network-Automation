
from flask import Flask, render_template, jsonify
from netmiko import ConnectHandler

app = Flask(__name__)


# CISCO ROUTER CONFIGURATION
router_device = {
    'device_type': 'cisco_ios_telnet',
    'ip': '192.168.10.225',
    'port': 32770,
    'username': 'admin',
    'password': 'eve123',
    'secret': 'eve123',

    'conn_timeout': 15,
    'auth_timeout': 20,
    'banner_timeout': 20,

    # Disable command echo verification
    'global_cmd_verify': False,
}


# COMMANDS TO EXECUTE
commands_to_run = [
    "show version",
    "show ip interface brief",
    "show running-config"
]


# DASHBOARD
@app.route("/")
def dashboard():
    return render_template("index.html")


# ROUTER API
@app.route("/api/execute", methods=["POST"])
def execute_commands():

    results = {}
    net_connect = None

    try:

        print("\nConnecting to Cisco Router...")

        net_connect = ConnectHandler(**router_device)

        print("Router connected successfully!")

        # ENTER ENABLE MODE
        net_connect.enable()

        # DISABLE PAGINATION
        net_connect.send_command_timing(
            "terminal length 0",
            read_timeout=15
        )

        # EXECUTE COMMANDS
        for cmd in commands_to_run:

            print(f"\nExecuting: {cmd}")

            output = net_connect.send_command_timing(
                cmd,
                read_timeout=60,
                last_read=3
            )

            results[cmd] = output

            print(output)

        return jsonify({
            "success": True,
            "message": "All router commands executed successfully!",
            "results": results
        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:

        if net_connect is not None:

            net_connect.disconnect()

            print("\nDisconnected successfully.")


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

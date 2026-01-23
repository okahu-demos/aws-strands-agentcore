import os
from time import sleep
from .demo_setup import setup_okahu, setup_agentcore_config, deploy_agentcore, okahu_discovery, run_agent_test, get_trace_url

def main():
    #check if first argument is --key, then set the OKAHU_API_KEY environment variable
    if len(os.sys.argv) > 2 and os.sys.argv[1] == '--key':
        os.environ['OKAHU_API_KEY'] = os.sys.argv[2]

    print("Starting Okahu Agentcore Demo Setup..." )

    # Step 1: Setup Okahu
    print("Setting up Okahu...")
    setup_okahu()
    print("Okahu setup completed.")
    sleep(1)

    # Step 2: Setup Agentcore configuration
    print("Setting up Agentcore ...")
    setup_agentcore_config()

    # Step 3: Deploy Agentcore
    deploy_agentcore()
    print("Agentcore deployment completed.")
    sleep(1)

    # Step 4: Run a test for the agent
    print("Testing agent deployment...")
    run_agent_test()
    print("Agent test completed.")
    sleep(1)

    # Step 5: Trigger Okahu discovery
    print("Updating Okahu tenant")
    sleep(2)
    okahu_discovery()
    print("Okahu update completed!!")

    print(os.linesep + "Demo setup completed successfully.")
    print("To test agent deployed via Agentcore CLI, run:")
    print("agentcore invoke '{\"prompt\": \"<prompt>\"}'")
    print("See travel agent traces in Okahu, goto - " + get_trace_url())

if __name__ == "__main__":
    main()
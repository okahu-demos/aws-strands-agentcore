from .demo_setup import setup_okahu, setup_agentcore_config, deploy_agentcore, okahu_discovery, run_agent_test

def main():
    # Step 1: Setup Okahu
###    setup_okahu()

    # Step 2: Setup Agentcore configuration
###    setup_agentcore_config()

    # Step 3: Deploy Agentcore
###    deploy_agentcore()

    # Step 4: Run a test for the agent
###    run_agent_test()

    # Step 5: Trigger Okahu discovery
    okahu_discovery()

    print("Demo setup completed successfully.")

if __name__ == "__main__":
    main()
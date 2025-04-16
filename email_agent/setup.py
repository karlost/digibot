from setuptools import setup, find_packages

setup(
    name="email_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-adk",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "email-agent=email_agent.agent:main",
            "email-agent-zerolab=email_agent.agent_zerolab:main",
        ],
    },
)

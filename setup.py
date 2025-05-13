from setuptools import setup, find_packages

setup(
    name='fc-prompt-tester',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'streamlit',
        'click',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'fc-test=cli.main:run_cli',
            'fc-ui=ui.dashboard:start_ui',
        ],
    },
)
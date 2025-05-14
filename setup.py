from setuptools import setup, find_packages

setup(
    name='fc-prompt-tester',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pyyaml>=6.0',
        'streamlit>=1.22.0',
        'click>=8.1.3',
        'rich>=13.0.0',
        'litellm>=0.1.1',
        'python-dotenv>=1.0.0',
        'jinja2>=3.1.2',
    ],
    extras_require={
        'dev': [
            'pytest>=7.3.1',
            'flake8>=6.0.0',
            'black>=23.3.0',
            'mypy>=1.3.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'fc-test=cli.main:run_cli',
            'fc-ui=ui.dashboard:start_ui',
            'fc-report=cli.commands:report',
            'fc-generate=cli.commands:generate',
            'fc-config=cli.commands:config',
        ],
    },
    python_requires='>=3.8',
    author='FC Prompt Tester Contributors',
    author_email='example@example.com',
    description='Tool for testing AI system prompts against various attack vectors',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/fc-prompt-tester',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
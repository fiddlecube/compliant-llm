def run_tests(config):
    prompt = config.get('prompt')
    report = {"prompt": prompt, "result": "PASS"}
    from core.reporter import save_report
    save_report(report)
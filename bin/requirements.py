import json

def convert_pipfile_lock_to_requirements(pipfile_lock_path):
    with open(pipfile_lock_path, 'r') as f:
        pipfile_lock = json.load(f)

    requirements = []
    for package in pipfile_lock['default']:
        package_name = package
        package_details = pipfile_lock['default'][package]
        version = package_details['version']
        markers = package_details.get('markers', '')
        if markers:
            markers = '; ' + markers
        requirement_line = f"{package_name}{version}{markers}"
        requirements.append(requirement_line)

    requirements_txt = '\n'.join(requirements) + '\n'  # Add a newline at the end
    return requirements_txt

if __name__ == '__main__':
    pipfile_lock_path = 'Pipfile.lock'
    requirements_txt = convert_pipfile_lock_to_requirements(pipfile_lock_path)
    print(requirements_txt)

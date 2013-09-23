import re
import os
from setuptools import setup, find_packages


def parse_requirements():
    """Rudimentary parser for the `requirements.txt` file

    We just want to separate regular packages from links to pass them to the
    `install_requires` and `dependency_links` params of the `setup()`
    function properly.
    """
    try:
        requirements = \
            map(str.strip, local_file('requirements.txt').splitlines())
    except IOError:
        raise RuntimeError("Couldn't find the `requirements.txt' file :(")

    links = []
    pkgs = []
    for req in requirements:
        if not req:
            continue
        if 'http:' in req or 'https:' in req:
            links.append(req)
            name, version = re.findall("\#egg=([^\-]+)-(.+$)", req)[0]
            pkgs.append('{0}=={1}'.format(name, version))
        else:
            pkgs.append(req)

    return pkgs, links

local_file = lambda f: \
    open(os.path.join(os.path.dirname(__file__), f)).read()

install_requires, dependency_links = parse_requirements()

if __name__ == '__main__':

    setup(
        name="graphite_aws_cleaner",
        version='0.0.3', # change __version__ also
        description=(
            "Delete old graphite data based on instance name pattern"
            "and current running AWS instances."),
        long_description=local_file('README.rst'),
        author='Yipit Coders',
        author_email='coders@yipit.com',
        url='https://github.com/Yipit/graphite_aws_cleaner',
        packages=find_packages(exclude=['*tests*']),
        install_requires=install_requires,
        dependency_links=dependency_links,
        entry_points={
            'console_scripts': ['graphite-aws-cleaner = graphite_aws_cleaner.cli:main'],
        },
        classifiers=[
            'Programming Language :: Python',
        ],
        zip_safe=False,
    )

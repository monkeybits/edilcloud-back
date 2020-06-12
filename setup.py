# http://www.28lines.com/?p=8

import os
import re
from setuptools import setup, find_packages
from setuptools.command.test import test


class TestRunner(test):

    def run(self, *args, **kwargs):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(
                self.distribution.tests_require)
        from web.tests.runtests import runtests

        runtests()


def get_data_files(*args, **kwargs):
    EXT_PATTERN = kwargs.get('ext') or '\.(html|js|txt|css|po|mo)'

    data_dict = {}
    for pkg_name in args:
        data_files = []
        for dirpath, dirnames, filenames in os.walk(pkg_name):
            rel_dirpath = re.sub("^" + pkg_name + '/', '', dirpath)
            # Ignore dirnames that start with '.'
            for i, dirname in enumerate(dirnames):
                if dirname.startswith('.'):
                    del dirnames[i]
            if filenames:
                data_files += [os.path.join(rel_dirpath, f) for f in filenames
                               if re.search(EXT_PATTERN, f)]
        data_dict[pkg_name] = data_files
    return data_dict


setup(
    name='office2017.whistle.it',
    version="1.0",
    description='THUX project',
    author='THUX',
    url='http://hg.thundersystems.it/jmb/office2017.whistle.it',
    author_email='dev@thundersystems.it',
    packages=find_packages(exclude=['tests', 'tests.*']),
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
        'Framework :: Jumbo',
    ],
    test_suite="web.tests",
    cmdclass={"test": TestRunner},
    install_requires=[
        'setuptools',
        'raven',
        'certifi==2017.4.17',
        'chardet==3.0.4',
        'coreapi==2.3.1',
        'coreschema==0.0.4',
        'decorator==4.0.11',
        'defusedxml==0.5.0',
        'dj-cmd==1.0.0',
        'Django==1.11.3',
        'django-allauth==0.32.0',
        'django-application-settings==0.2',
        'django-cors-headers==2.1.0',
        'django-debug-toolbar==1.8',
        'django-extensions==1.7.9',
        'django-flat-responsive==1.4.1',
        'django-mptt==0.8.7',
        'django-rest-auth==0.9.1',
        'djangorestframework==3.6.3',
        'djangorestframework-jwt==1.11.0',
        'docutils==0.13.1',
        'drfdocs==0.0.11',
        'Faker==0.7.18',
        'idna==2.5',
        'ipdb==0.10.3',
        'ipython==5.1.0',
        'ipython-genutils==0.2.0',
        'itypes==1.1.0',
        'jedi==0.10.2',
        'Jinja2==2.9.6',
        'MarkupSafe==1.0',
        'oauthlib==2.0.2',
        'olefile==0.44',
        'openapi-codec==1.3.1',
        'pexpect==4.2.1',
        'pickleshare==0.7.4',
        'Pillow==4.1.1',
        'prompt-toolkit==1.0.14',
        'psycopg2',
        'ptyprocess==0.5.1',
        'pydot==1.2.3',
        'Pygments==2.2.0',
        'pyparsing==2.2.0',
        'python3-openid==3.1.0',
        'pytz==2017.2',
        'requests==2.18.1',
        'requests-oauthlib==0.8.0',
        'simplegeneric==0.8.1',
        'simplejson==3.11.1',
        'six==1.10.0',
        'sqlparse==0.2.3',
        'traitlets==4.3.2',
        'typing==3.6.1',
        'uritemplate==3.0.0',
        'urllib3==1.21.1',
        'wcwidth==0.1.7',
        'python-magic==0.4.13',
        'rest-social-auth==1.2.0',
        'xlrd==1.1.0'
    ],
    package_data=get_data_files('web')
)

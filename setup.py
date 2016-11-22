from setuptools import setup, find_packages

setup(
    name='Flask-GeoIP2',
    version='0.0.1',
    description='http://github.com/vgavro/flask-geoip2',
    long_description='http://github.com/vgavro/flask-geoip2',
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Victor Gavro',
    author_email='vgavro@gmail.com',
    url='http://github.com/vgavro/flask-geoip2',
    keywords='',
    packages=find_packages(),
    install_requires=['flask>=0.9', 'geoip2'],
)

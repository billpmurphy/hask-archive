try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

description = "We put a Haskell in your Python so you can Haskell while you Python."
setup(
        name = 'hask',
        version = fn.__version__,
        description=description,
        long_description = open('README.md').read(),
        author='Bill Murphy',
        #author_email='',
        url='https://github.com/billpmurphy/pythaskell',
        packages=['hask'],
        package_data={'': ['LICENSE', 'README.md']},
        include_package_data=True,
        install_requires=[],
        license=open('LICENSE').read(),
        zip_safe=False,
        classifiers=(
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7'
            ),
        )

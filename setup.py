import setuptools

setuptools.setup(
    name='viddit',
    package_dir={'': 'src'},
    package_data={
        'viddit': ['resources/*']
    },
    include_package_data=True,
    install_requires=["opencv-python", "selenium", "moviepy", "numpy", "oauth2client","google-cloud-texttospeech", "gTTS", "google-api-python-client", "google-auth-oauthlib", "openai", "google-auth-httplib2", "pymongo", "praw", "pydrive"],
    packages=setuptools.find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'viddit=viddit.__main__:main',
        ],
    },
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
	python_requires='>=3.7',
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    author='James Massey',
    author_email='jammassey@hotmail.com',
)
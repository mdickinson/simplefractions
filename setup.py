# Copyright 2020 Mark Dickinson. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name="simplefractions",
    version="1.0.0",
    author="Mark Dickinson",
    author_email="dickinsm@gmail.com",
    description="Find the simplest fraction for a given float or interval",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mdickinson/simplefractions",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.6",
)

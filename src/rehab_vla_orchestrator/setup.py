from setuptools import setup

package_name = "rehab_vla_orchestrator"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="HalloYang06",
    maintainer_email="2735283977@qq.com",
    description="Dry-run VLA loop orchestrator for rehab arm modes",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "rehab_vla_orchestrator = rehab_vla_orchestrator.orchestrator_node:main",
        ],
    },
)

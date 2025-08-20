Related Projects
================

This package is part of a broader ecosystem of knitting software and research projects. This page provides an overview of related tools, libraries, and research initiatives.

🧶 Northeastern ACT Lab Knitting Ecosystem
------------------------------------------

KnitScript is developed as part of the Northeastern University ACT Lab's comprehensive knitting software ecosystem. These projects work together to provide end-to-end knitting machine programming capabilities.

Core Knitting Libraries
~~~~~~~~~~~~~~~~~~~~~~~

**knit-graphs** |knit_graphs_version|
   Knitting graph data structures and analysis tools.

   - **Purpose**: Models fabric topology and stitch relationships
   - **Key Features**: Stitch dependency tracking, fabric analysis, pattern validation
   - **Integration**: Used by KnitScript to represent generated fabric structures
   - **Repository**: `knit-graphs on PyPI <https://pypi.org/project/knit-graphs/>`_

**knit-script** |vkm_version|
   A general purpose machine knitting langauge

   - **Purpose**: Fully programmatic support to control knitting machines.
   - **Repository**: `knit-script on PyPI <https://pypi.org/project/knit-script/>`_

**knitout-interpreter** |knitout_interp_version|
   Knitout processing and execution framework.

   - **Purpose**: Processes and validates knitout instruction files
   - **Key Features**: Instruction parsing, carriage pass organization, error detection
   - **Integration**: Processes KnitScript's generated knitout output
   - **Repository**: `knitout-interpreter on PyPI <https://pypi.org/project/knitout-interpreter/>`

Optimization and Analysis Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**koda-knitout** |koda_version|
   Optimization framework for knitout instructions.

   - **Purpose**: Optimizes knitout files for faster execution and better quality
   - **Key Features**: Carriage pass optimization, instruction reordering, resource minimization
   - **Integration**: Can post-process KnitScript's generated knitout for optimization
   - **Repository**: `koda-knitout on PyPI <https://pypi.org/project/koda-knitout/>`_

.. |knit_graphs_version| image:: https://img.shields.io/pypi/v/knit-graphs.svg
   :target: https://pypi.org/project/knit-graphs/

.. |vkm_version| image:: https://img.shields.io/pypi/v/knit-script.svg
   :target: https://pypi.org/project/knit-script/

.. |knitout_interp_version| image:: https://img.shields.io/pypi/v/knitout-interpreter.svg
   :target: https://pypi.org/project/knitout-interpreter/

.. |koda_version| image:: https://img.shields.io/pypi/v/koda-knitout.svg
   :target: https://pypi.org/project/koda-knitout/

🏛️ CMU Textiles Lab
--------------------

KnitScript builds upon foundational work from Carnegie Mellon University's Textiles Lab, which created the knitout specification and ecosystem.

Original Knitout Specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**knitout**
   The original knitout specification and reference implementation.

   - **Purpose**: Low-level instruction format for V-bed knitting machines
   - **Key Features**: Machine-independent instruction set, standardized format
   - **Documentation**: `Knitout Specification <https://textiles-lab.github.io/knitout/knitout.html>`_

🎓 Educational and Research Use
-------------------------------

Academic Adoption
~~~~~~~~~~~~~~~~~

KnitScript is used in educational and research contexts:

**Courses and Workshops:**
   - Digital fabrication courses
   - Computational design programs
   - Textile engineering curricula
   - Creative coding workshops

**Research Applications:**
   - Smart textile development
   - Automated pattern generation
   - Machine learning for knitting
   - Optimization algorithm research

**Student Projects:**
   - Senior capstone projects
   - Graduate research theses
   - Hackathon and competition entries
   - Cross-disciplinary collaborations

Collaboration Opportunities
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For Researchers:**
   - Access to advanced knitting programming tools
   - Integration with existing research workflows
   - Collaboration with ACT Lab team
   - Publication and conference opportunities

**For Educators:**
   - Course material and example patterns
   - Workshop templates and curricula
   - Student project ideas and frameworks
   - Assessment rubrics and evaluation tools

**For Industry:**
   - Rapid prototyping capabilities
   - Custom pattern development tools
   - Integration with existing workflows
   - Training and consulting services

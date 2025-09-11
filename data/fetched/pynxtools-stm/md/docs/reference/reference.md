# References
To get the full benefits of the reader, you can visit and utilize the following tools and platforms. 

## NOMAD
The reader is fully integrated into the [NOMAD](https://nomad-lab.eu/prod/v1/gui/about/information) research data management platform (a free and open sorce project for data management). In NOMAD, you can find a full example for both the `STS` as well as the `STM` reader. The example can be resused to create new uploads and later the uploads can be compared, analyzed, publihsed, and shared with the different colaborators and communities. You can have a look at the [NOMAD documentation](https://nomad-lab.eu/prod/v1/util/docs/index.html) as well.

## NeXus
The reader is using the [NXsts](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXsts.html#nxsts) ([GitHub page](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml)) application definition (as a standardized schema) which is developed using the [NeXus ontology](https://www.nexusformat.org/) ([GitHub page](https://github.com/FAIRmat-NFDI/nexus_definitions/tree/fairmat)). To understand the application definition, properly understanding NeXus ontology can be helpful.

## STS Reader
The main goal of the STS Reader is to transform different file formats from diverse STS lab into STS community standard [STS application definition](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml), community defined template that define indivisual concept associated with STS experiment constructed by SPM community.
## STS Example
There are diverse examples for several versions (Generic 5e and Generic 4.5) of the Nanonis software for STS experiments at [https://gitlab.mpcdf.mpg.de](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-remote-tools-hub/-/tree/develop/docker/sts). But, to utilize that examples one must have an account at https://gitlab.mpcdf.mpg.de. If still you want to try out the examples from the STS reader, please reach out to [Rubel Mozumder](mozumder@physik.hu-berlin.de) or the docker container (discussed below).

To get a detailed overview of the sts reader implementation visit [pynxtools-stm](https://github.com/FAIRmat-NFDI/pynxtools-stm).

## STS docker image
STS docker image contains all prerequisite tools (e.g. jupyter-notebook) and library to run STS reader. To use the image user needs to [install docker engine](https://docs.docker.com/engine/install/).

STS Image: `gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-remote-tools-hub/sts-jupyter:latest`

To run the STS image as a docker container copy the code below in a file `docker-compose.yaml`

```docker
# docker-compose.yaml
version: "3.9"
services:
    sts:
        image: gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-remote-tools-hub/sts-jupyter:latest
        ports:
            - 8888:8888
        volumes:
            - ./example:/home/jovyan/work_dir
        working_dir: /home/jovyan/work_dir
```

and launch the file from the same directory with `docker compose up` command.
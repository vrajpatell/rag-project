from rag_project.services.factory import ServiceFactory


def get_factory() -> ServiceFactory:
    return ServiceFactory.get()

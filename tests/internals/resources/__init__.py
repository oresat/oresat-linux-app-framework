import canopen
from oresat_configs import NodeId, OreSatConfig, OreSatId

from olaf import OreSatFileCache, Resource, logger
from olaf._internals.node import Node

logger.disable("olaf")


class MockNode(Node):
    """Mock node for testing Resources."""

    def __init__(self):
        od = OreSatConfig(OreSatId.ORESAT0).od_db[NodeId.GPS]
        super().__init__(od, None)

        self._fread_cache = OreSatFileCache("/tmp/fread")
        self._fread_cache.clear()
        self._fwrite_cache = OreSatFileCache("/tmp/fwrite")
        self._fwrite_cache.clear()

        self._setup_node()

    def send_tpdo(self, tpdo: int):
        pass  # override to do nothing


class MockApp:
    """Mock app for testing Resources."""

    def __init__(self):
        super().__init__()

        self.node = MockNode()
        self.resource = None

    def add_resource(self, resource: Resource):
        """Add the resource for testing"""

        self.resource = resource

    def sdo_read(self, index: [int, str], subindex: [None, int, str]):
        """Call a internal SDO read for testing"""

        co_node = self.node._node
        domain = canopen.objectdictionary.DOMAIN

        if subindex is None:
            if co_node.object_dictionary[index].data_type == domain:
                return co_node.sdo[index].raw
            else:
                return co_node.sdo[index].phys
        else:
            if co_node.object_dictionary[index][subindex].data_type == domain:
                return co_node.sdo[index][subindex].raw
            else:
                return co_node.sdo[index][subindex].phys

    def sdo_write(self, index: [int, str], subindex: [None, int, str], value):
        """Call a internal SDO write for testing"""

        co_node = self.node._node
        domain = canopen.objectdictionary.DOMAIN

        if subindex is None:
            if co_node.object_dictionary[index].data_type == domain:
                co_node.sdo[index].raw = value
            else:
                co_node.sdo[index].phys = value
        else:
            if co_node.object_dictionary[index][subindex].data_type == domain:
                co_node.sdo[index][subindex].raw = value
            else:
                co_node.sdo[index][subindex].phys = value

    def start(self):
        self.resource.start(self.node)

    def stop(self):
        self.resource.end()
        self.node._destroy_node()
        self.node.stop()

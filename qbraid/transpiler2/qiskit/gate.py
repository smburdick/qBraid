from typing import Union, Iterable

from ..gate import AbstractGate
from .utils import get_qiskit_gate_data

from qiskit.circuit.gate import Gate
from qiskit.circuit import Parameter

class QiskitGateWrapper(AbstractGate):
    def __init__(self, gate: Gate, params: Union[int,Iterable[int]] = None):

        super().__init__()

        self.gate = gate
        self.params = params
        self.name = gate.name

        data = get_qiskit_gate_data(gate)

        self.matrix = data["matrix"]
        # self.params = data['params']
        self.num_controls = data["num_controls"]

        self._gate_type = data["type"]
        self._outputs["qiskit"] = gate
        self.package = "qiskit"

    def get_abstract_params(self):
        return [p for p in self.params if isinstance(p,Parameter)]

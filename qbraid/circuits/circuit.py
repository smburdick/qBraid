from typing import Union, Iterable

from .update_rule import UpdateRule
from .instruction import Instruction
from .moment import Moment
from .qubit import Qubit
from .utils import validate_operation
from .exceptions import CircuitError


class Circuit:

    """
    Circuit class for qBraid quantum circuit objects.
    Args:
        num_qubits: The total number of qubits
        name: The name of the circuit
        update_rule: How to pick/create the moment to put operations into.
    """

    def __init__(
        self,
        num_qubits,
        name: str = None,
        update_rule: UpdateRule = UpdateRule.NEW_THEN_INLINE,
    ):
        self._qubits = [Qubit(i) for i in range(num_qubits)]
        self._moments: Iterable[Moment] = []  # list of moments
        self.name = name
        self.update_rule = update_rule

    @property
    def num_qubits(self):
        return len(self._qubits)

    @property
    def num_gates(self):
        raise NotImplementedError

    @property
    def moments(self):
        return self._moments

    @property
    def instructions(self):

        instructions_list = []
        for moment in self._moments:
            instructions_list.append(moment.instructions)

        return instructions_list

    def _append(self, moments: Union[Moment, Iterable[Moment]]):

        if isinstance(moments, Moment):
            moments = [moments]
        # validate moment
        for moment in moments:
            if max(moment.qubits) > self.num_qubits:
                raise CircuitError(
                    "Index {} exceeds number of qubits {} in circuit".format(
                        moment.qubits, self.num_qubits
                    )
                )
        self._moments.extend(moments)

    def _append_circuit(self, operation, mapping: Union[list, dict]) -> None:

        """this is for adding subroutines to circuits. so if we have a 3-qubit subroutine,
        the user should specify [2,4,5], implying that qubit 0 on the subroutine is mapped
        to qubit 2 on the circuit, qubit 1 on the subroutine maps to qubit 4 on the circuit, etc.
        
        the user should also be able to specify directly as a dict:
            {0:2,1:4,5:5}
            
            qiskit has two gate operation that, 
            circuit can just append moments (still need moments)
            extend(**unzipped moments)
        """

        # TODO: validate mapping
        # TODO: develop appending strategy for an entire circuit.

        raise NotImplementedError

    def _earliest_appended(self, op) -> bool:
        appended = False
        # scan through the moments beginning with the first moment
        for moment in self._moments:
            moment.append(op)
            appended = True
        return appended

    def _create_new_moment(self, op=None):
        """"create a new moment every time append is called and append the operation."""
        new_moment = Moment()
        if op:
            new_moment.instructions.append(op)
        self._moments.append(new_moment)

    def _update(
        self, operation: Union[Moment, Iterable[Instruction]], update_rule, index=0
    ) -> None:
        """ Cycles through all the operations and appends to circuit according to update rule."""
        # takes in both moment and instructions
        for op in operation:
            if isinstance(op, Instruction):
                if validate_operation(op):
                    if update_rule is UpdateRule.NEW_THEN_INLINE:
                        # add new
                        self._create_new_moment(op)
                        # update_rule changes to INLINE
                        update_rule = UpdateRule.INLINE
                    elif update_rule is UpdateRule.INLINE:
                        # the last moment in the circuit
                        curr_moment = self._moments[-1]
                        if curr_moment.appendable(op):
                            curr_moment.append(op)
                        else:
                            # create a new moment
                            self._create_new_moment(op)
                    elif update_rule is UpdateRule.NEW:
                        # create a new moment every time append is called
                        self._create_new_moment(op)
                    elif update_rule is UpdateRule.EARLIEST:
                        if not self._earliest_appended(op):
                            self._create_new_moment(op)
            elif isinstance(op, Moment):
                # limit index to 0..len(self._moments), also deal with indices smaller 0
                k = max(
                    min(
                        index if index >= 0 else len(self._moments) + index,
                        len(self._moments),
                    ),
                    0,
                )
                # moments don't need a strategy.
                self.moments.insert(k, operation)
                k += 1

    def append(
        self,
        operation: Union[Instruction, Moment, Iterable[Instruction], Iterable[Moment]],
        mapping: Union[list, dict] = None,
        update_rule: UpdateRule = None,
    ) -> None:
        """
        Appends an operation (moment or instruction) to the circuit.
        Args:
            operation: The moment/instruction or iterable of moment/instructions to append.
            mapping: An iterable with the qubits which the operation acts upon.
            update_rule: How to pick/create the moment to put operations into.
        """
        if operation is None:
            raise TypeError(
                "Operation of type {} not appendable".format(type(operation))
            )  # redundant
        if update_rule is None:
            update_rule = self.update_rule
        if not self._moments:
            # initialize a new moment
            self._create_new_moment()
        # iterable
        if isinstance(operation, Iterable):
            self._update(operation, update_rule=update_rule, index=len(self._moments))
        elif isinstance(operation, Circuit):
            # not implemented
            self._append_circuit(
                operation, mapping,
            )
        else:
            # make operation into interable and attempt to append.
            self.append(operation=[operation], mapping=mapping, update_rule=update_rule)

    def __len__(self):
        return len(self._moments)

    def __str__(self):
        print(f"Circuit with {self.num_qubits} and {self.num_gates}")

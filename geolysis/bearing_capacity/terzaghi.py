from dataclasses import dataclass

from geolysis import GeotechEng
from geolysis.bearing_capacity import FoundationSize
from geolysis.utils import PI, arctan, cos, deg2rad, exp, round_, tan


@dataclass
class TerzaghiBearingCapacityFactors:
    soil_friction_angle: float
    eng: GeotechEng = GeotechEng.MEYERHOF

    @property
    @round_(precision=2)
    def nc(self) -> float:
        r"""Return ``Terzaghi`` bearing capacity factor :math:`N_c`.

        .. math::

            N_c = \cot \phi \left(N_q - 1 \right)

        """
        x_1 = 1 / tan(self.soil_friction_angle)
        x_2 = self.nq - 1

        return x_1 * x_2

    @property
    @round_(precision=2)
    def nq(self) -> float:
        r"""Return ``Terzaghi`` bearing capacity factor :math:`N_q`.

        .. math::

            N_q = \dfrac{e^{(\frac{3\pi}{2}-\phi)\tan\phi}}
                  {2\cos^2\left(45^{\circ}+\frac{\phi}{2}\right)}

        """
        x_1 = (3 * PI) / 2 - deg2rad(self.soil_friction_angle)
        x_2 = 2 * (cos(45 + (self.soil_friction_angle / 2)) ** 2)

        return exp(x_1 * tan(self.soil_friction_angle)) / x_2

    @property
    @round_(precision=2)
    def ngamma(self) -> float:
        r"""Return ``Terzaghi`` bearing capacity factor :math:`N_\gamma`.

        .. note::

            Exact values of :math:`N_\gamma` are not directly obtainable; values have
            been proposed by ``Brinch Hansen (1968)`` which are widely used in Europe,
            and also by ``Meyerhof (1963)``, which have been adopted in North America.

        The formulas shown below are ``Brinch Hansen`` and ``Meyerhof`` respectively.

        .. math::

            N_\gamma &= 1.8 \left(N_q - 1 \right) \tan \phi

            N_\gamma &= \left(N_q -1 \right)\tan(1.4\phi)

        """
        _ngamma: float

        if self.eng is GeotechEng.MEYERHOF:
            _ngamma = (self.nq - 1) * tan(1.4 * self.soil_friction_angle)

        elif self.eng is GeotechEng.HANSEN:
            _ngamma = 1.8 * (self.nq - 1) * tan(self.soil_friction_angle)

        else:
            msg = f"Available types are {GeotechEng.MEYERHOF} or {GeotechEng.HANSEN}"
            raise TypeError(msg)

        return _ngamma


class TerzaghiBearingCapacity:
    r"""Ultimate bearing capacity according to ``Terzaghi`` for ``strip``,
    ``square``, ``rectangular`` and ``circular footing``.

    :Example:


    :param cohesion: cohesion of foundation soil :math:`(kN/m^2)`
    :type cohesion: float
    :param friction_angle: internal angle of friction (degrees)
    :type soil_friction_angle: float
    :param soil_unit_weight: unit weight of soil :math:`(kN/m^3)`
    :type soil_unit_weight: float
    :param foundation_depth: depth of foundation :math:`d_f` (m)
    :type foundation_depth: float
    :param foundation_width: width of foundation (**B**) (m)
    :type foundation_width: float
    :param eng: specifies the type of ngamma formula to use. Available
                values are geolab.MEYERHOF and geolab.HANSEN
    :type eng: GeotechEng
    """

    def __init__(
        self,
        *,
        cohesion: float,
        soil_friction_angle: float,
        soil_unit_weight: float,
        foundation_size: FoundationSize,
        eng: GeotechEng = GeotechEng.MEYERHOF,
    ) -> None:
        self.cohesion = cohesion
        self.soil_friction_angle = soil_friction_angle

        self.soil_unit_weight = soil_unit_weight
        self.foundation_size = foundation_size
        self.footing_size = self.foundation_size.footing_size
        self.eng = eng

        self.bearing_capacity_factor = TerzaghiBearingCapacityFactors(
            self.soil_friction_angle, self.eng
        )

    @property
    def _x_1(self) -> float:
        return self.cohesion * self.nc

    @property
    def _x_2(self) -> float:
        return self.soil_unit_weight * self.foundation_size.depth * self.nq

    @property
    def _x_3(self) -> float:
        return self.soil_unit_weight * self.foundation_size.width * self.ngamma

    def local_shear(self):
        self.cohesion = (2 / 3) * self.cohesion
        self.soil_friction_angle = arctan(
            (2 / 3) * tan(self.soil_friction_angle)
        )

    @round_
    def ultimate_4_strip_footing(self) -> float:
        r"""Return ultimate bearing capacity of strip footings.

        .. math::

            q_u = c \cdot N_c + \gamma
                  \cdot D_f \cdot N_q
                  + 0.5 \cdot \gamma \cdot B \cdot N_\gamma
        """
        return self._x_1 + self._x_2 + 0.5 * self._x_3

    @round_
    def ultimate_4_square_footing(self) -> float:
        r"""Return ultimate bearing capacity for square footings.

        .. math::

            q_u = 1.3 \cdot c \cdot N_c
                  + \gamma \cdot D_f \cdot N_q
                  + 0.4 \cdot \gamma \cdot B \cdot N_\gamma
        """
        return 1.3 * self._x_1 + self._x_2 + 0.4 * self._x_3

    @round_
    def ultimate_4_circular_footing(self) -> float:
        r"""Return ultimate bearing capacity for circular footing.

        .. math::

            q_u = 1.3 \cdot c \cdot N_c
                  + \gamma \cdot D_f \cdot N_q
                  + 0.3 \cdot \gamma \cdot B \cdot N_\gamma
        """
        return 1.3 * self._x_1 + self._x_2 + 0.3 * self._x_3

    @round_
    def ultimate_4_rectangular_footing(self) -> float:
        r"""Return the ultimate bearing for rectangular footing.

        .. math::

            q_u = \left( 1 + 0.3 \cdot \dfrac{B}{L} \right) c \cdot N_c
                  + \gamma \cdot D_f \cdot N_q
                  + \dfrac{1}{2} \left(1 - 0.2 \cdot \dfrac{B}{L} \right)
                  \cdot \gamma \cdot B \cdot N_\gamma
        """
        a = 1 + 0.3 * (self.footing_size.width / self.footing_size.length)
        b = 0.5 * (
            1 - 0.2 * self.footing_size.width / self.footing_size.length
        )

        return a * self._x_1 + self._x_2 + b * self._x_3

    @property
    def nc(self) -> float:
        return self.bearing_capacity_factor.nc

    @property
    def nq(self) -> float:
        return self.bearing_capacity_factor.nq

    @property
    def ngamma(self) -> float:
        return self.bearing_capacity_factor.ngamma
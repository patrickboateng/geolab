from dataclasses import dataclass

from geolab import GeotechEng
from geolab.bearing_capacity import FootingShape, FootingSize, FoundationSize
from geolab.utils import PI, arctan, cos, deg2rad, exp, sin, tan


@dataclass
class terzaghi_bearing_capacity_factors:
    soil_friction_angle: float
    eng: GeotechEng = GeotechEng.MEYERHOF

    @property
    def nc(self) -> float:
        """Returns ``Terzaghi`` bearing capacity factor :math:`N_c`."""
        x1 = 1 / tan(self.soil_friction_angle)
        x2 = self.nq - 1

        return x1 * x2

    @property
    def nq(self) -> float:
        """Returns ``Terzaghi`` bearing capacity factor :math:`N_q`."""
        x1 = (3 * PI) / 2 - deg2rad(self.soil_friction_angle)
        x2 = 2 * (cos(45 + (self.soil_friction_angle / 2)) ** 2)

        return exp(x1 * tan(self.soil_friction_angle)) / x2

    @property
    def ngamma(self) -> float:
        r"""Returns ``Terzaghi`` bearing capacity factor :math:`N_\gamma`."""
        _ngamma: float

        if self.eng is GeotechEng.MEYERHOF:
            _ngamma = (self.nq - 1) * tan(1.4 * self.soil_friction_angle)

        elif self.eng is GeotechEng.HANSEN:
            _ngamma = 1.8 * (self.nq - 1) * tan(self.soil_friction_angle)

        else:
            msg = f"Available types are {GeotechEng.MEYERHOF} or {GeotechEng.HANSEN}"
            raise TypeError(msg)

        return _ngamma


class terzaghi_bearing_capacity:
    r"""Ultimate bearing capacity according to ``Terzaghi`` for ``strip footing``,
    ``square footing`` and ``circular footing``.

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
        cohesion: float,
        soil_friction_angle: float,
        soil_unit_weight: float,
        foundation_size: FoundationSize,
        eng: GeotechEng = GeotechEng.MEYERHOF,
    ) -> None:
        self.cohesion = cohesion
        self.soil_unit_weight = soil_unit_weight
        self.foundation_size = foundation_size
        self.soil_friction_angle = soil_friction_angle
        self.eng = eng

        self.bcf = terzaghi_bearing_capacity_factors(
            self.soil_friction_angle, self.eng
        )

    def ultimate_4_strip_footing(self) -> float:
        x1 = self.cohesion * self.nc
        x2 = self.soil_unit_weight * self.foundation_size.depth * self.nq
        x3 = self.soil_unit_weight * self.foundation_size.width * self.ngamma

        return x1 + x2 + 0.5 * x3

    def ultimate_4_square_footing(self) -> float:
        x1 = 1.3 * self.cohesion * self.nc
        x2 = self.soil_unit_weight * self.foundation_size.depth * self.nq
        x3 = self.soil_unit_weight * self.foundation_size.width * self.ngamma

        return x1 + x2 + 0.4 * x3

    def ultimate_4_circular_footing(self) -> float:
        x1 = 1.3 * self.cohesion * self.nc
        x2 = self.soil_unit_weight * self.foundation_size.depth * self.nq
        x3 = self.soil_unit_weight * self.foundation_size.width * self.ngamma

        return x1 + x2 + 0.3 * x3

    @property
    def nc(self) -> float:
        return self.bcf.nc

    @property
    def nq(self) -> float:
        return self.bcf.nq

    @property
    def ngamma(self) -> float:
        return self.bcf.ngamma


class meyerhof_bearing_capacity_factors:
    def __init__(self, soil_friction_angle: float):
        self.soil_friction_angle = soil_friction_angle

    @property
    def nc(self) -> float:
        """Returns ``Meyerhof`` bearing capacity factor :math:`N_c`."""
        return (1 / tan(self.soil_friction_angle)) * (self.nq - 1)

    @property
    def nq(self) -> float:
        """Returns ``Meyerhof`` bearing capacity factor :math:`N_q`."""
        x1 = tan(45 + self.soil_friction_angle / 2) ** 2
        x2 = exp(PI * tan(self.soil_friction_angle))

        return x1 * x2

    @property
    def ngamma(self) -> float:
        r"""Returns ``Meyerhof`` bearing capacity factor :math:`N_\gamma`."""
        return 2 * (self.nq + 1) * tan(self.soil_friction_angle)


@dataclass
class meyerhof_depth_factors:
    soil_friction_angle: float
    foundation_size: FoundationSize

    @property
    def depth_2_width_ratio(self) -> float:
        return self.foundation_size.depth_2_width_ratio

    @property
    def dc(self) -> float:
        """Returns ``Meyerhof`` depth factor :math:`d_c`."""
        _dc: float

        if self.depth_2_width_ratio <= 1:
            _dc = 1 + 0.4 * self.depth_2_width_ratio

        else:
            x1 = 0.4 * arctan(self.depth_2_width_ratio)
            _dc = 1 + x1 * (PI / 180)

        return _dc

    @property
    def dq(self) -> float:
        """Returns ``Meyerhof`` depth factor :math:`d_q`."""
        _dq: float

        x2 = (1 - sin(self.soil_friction_angle)) ** 2

        if self.depth_2_width_ratio <= 1:
            x1 = 2 * tan(self.soil_friction_angle)
            _dq = 1 + x1 * x2 * self.depth_2_width_ratio

        else:
            x1 = 2 * tan(self.soil_friction_angle)
            x3 = arctan(self.depth_2_width_ratio)
            _dq = 1 + x1 * x2 * x3 * (PI / 180)

        return _dq

    @property
    def dgamma(self) -> float:
        r"""Returns ``Meyerhof`` depth factor :math:`d_\gamma`."""
        return 1


@dataclass
class meyerhof_shape_factors:
    soil_friction_angle: float
    footing_size: FootingSize
    nq: float
    nc: float

    @property
    def width_2_length_ratio(self) -> float:
        return self.footing_size.width_2_length_ratio

    @property
    def sc(self) -> float:
        """Returns ``Meyerhof`` shape factor :math:`s_c`."""
        return 1 + self.width_2_length_ratio * (self.nq / self.nc)

    @property
    def sq(self) -> float:
        """Returns ``Meyerhof`` shape factor :math:`s_q`."""
        return 1 + self.width_2_length_ratio * tan(self.soil_friction_angle)

    @property
    def sgamma(self) -> float:
        r"""Returns ``Meyerhof`` shape factor :math:`s_\gamma`."""
        return 1 - 0.4 * self.width_2_length_ratio


@dataclass
class meyerhof_inclination_factors:
    soil_friction_angle: float
    beta: float

    @property
    def ic(self) -> float:
        """Returns ``Meyerhof`` inclination factor :math:`i_c`."""
        return (1 - self.beta / 90) ** 2

    @property
    def iq(self) -> float:
        """Returns ``Meyerhof`` inclination factor :math:`i_q`."""
        return self.ic

    @property
    def igamma(self) -> float:
        r"""Returns ``Meyerhof`` inclination factor :math:`i_\gamma`."""
        return (1 - self.beta / self.soil_friction_angle) ** 2


class meyerhof_bearing_capacity:
    def __init__(
        self,
        cohesion: float,
        soil_unit_weight: float,
        foundation_size: FoundationSize,
        soil_friction_angle: float,
        beta: float,
    ) -> None:
        self.cohesion = cohesion
        self.soil_unit_weight = soil_unit_weight
        self.foundation_size = foundation_size
        self.soil_friction_angle = soil_friction_angle
        self.beta = beta

        self.bearing_cpty_factors = meyerhof_bearing_capacity_factors(
            self.soil_friction_angle
        )
        self.depth_factors = meyerhof_depth_factors(
            self.soil_friction_angle, self.foundation_size
        )
        self.shape_factors = meyerhof_shape_factors(
            self.soil_friction_angle,
            self.foundation_size.footing_size,
            self.nq,
            self.nc,
        )
        self.incl_factors = meyerhof_inclination_factors(
            self.soil_friction_angle, self.beta
        )

    def __call__(self) -> float:
        return self.ultimate()

    def ultimate(self) -> float:
        r"""Returns the ultimate bearing capacity according to ``Hansen``."""
        x1 = self.cohesion * self.nc * self.sc * self.dc * self.ic
        x2 = self.soil_unit_weight * self.foundation_size.depth
        x3 = self.nq * self.sq * self.dq * self.iq
        x4 = self.soil_unit_weight * self.foundation_size.width
        x5 = self.ngamma * self.sgamma * self.dgamma * self.igamma

        return x1 + (x2 * x3) + (0.5 * x4 * x5)

    @property
    def nc(self) -> float:
        return self.bearing_cpty_factors.nc

    @property
    def nq(self) -> float:
        return self.bearing_cpty_factors.nq

    @property
    def ngamma(self) -> float:
        return self.bearing_cpty_factors.ngamma

    @property
    def dc(self) -> float:
        return self.depth_factors.dc

    @property
    def dq(self) -> float:
        return self.depth_factors.dq

    @property
    def dgamma(self) -> float:
        return self.depth_factors.dgamma

    @property
    def sc(self) -> float:
        return self.shape_factors.sc

    @property
    def sq(self) -> float:
        return self.shape_factors.sq

    @property
    def sgamma(self) -> float:
        return self.shape_factors.sgamma

    @property
    def ic(self) -> float:
        return self.incl_factors.ic

    @property
    def iq(self) -> float:
        return self.incl_factors.iq

    @property
    def igamma(self) -> float:
        return self.incl_factors.igamma


@dataclass
class hansen_bearing_capacity_factors:
    soil_friction_angle: float

    @property
    def nc(self) -> float:
        """Returns ``Hansen`` bearing capacity factor :math:`N_c`."""
        x1 = 1 / tan(self.soil_friction_angle)
        x2 = self.nq - 1.0

        return x1 * x2

    @property
    def nq(self) -> float:
        """Returns ``Hansen`` bearing capacity factor :math:`N_q`."""
        x1 = tan(45 + self.soil_friction_angle / 2) ** 2
        x2 = exp(PI * tan(self.soil_friction_angle))

        return x1 * x2

    @property
    def ngamma(self) -> float:
        r"""Returns ``Hansen`` bearing capacity factor :math:`N_\gamma`."""
        return 1.8 * (self.nq - 1.0) * tan(self.soil_friction_angle)


@dataclass
class hansen_depth_factors:
    foundation_size: FoundationSize

    @property
    def depth_2_width_ratio(self) -> float:
        return self.foundation_size.depth_2_width_ratio

    @property
    def dc(self) -> float:
        """Returns ``Hansen`` depth factor :math:`d_c`."""
        return 1 + 0.35 * self.depth_2_width_ratio

    @property
    def dq(self) -> float:
        """Returns ``Hansen`` depth factor :math:`d_q`."""
        return self.dc

    @property
    def dgamma(self) -> float:
        r"""Returns ``Hansen`` depth factor :math:`d_\gamma`."""
        return 1.0


@dataclass
class hansen_shape_factors:
    footing_size: FootingSize
    footing_shape: FootingShape

    @property
    def width_2_length_ratio(self) -> float:
        return self.footing_size.width_2_length_ratio

    @property
    def sc(self) -> float:
        """Returns ``Hansen`` shape factor :math:`s_c`."""
        _sc: float

        if self.footing_shape is FootingShape.STRIP:
            _sc = 1.0

        elif (
            self.footing_shape is FootingShape.SQUARE
            or self.footing_shape is FootingShape.CIRCULAR
        ):
            _sc = 1.3

        elif self.footing_shape is FootingShape.RECTANGULAR:
            _sc = 1 + 0.2 * self.width_2_length_ratio

        else:
            msg = ""
            raise TypeError(msg)

        return _sc

    @property
    def sq(self) -> float:
        """Returns ``Hansen`` shape factor :math:`s_q`."""
        _sq: float

        if self.footing_shape is FootingShape.STRIP:
            _sq = 1.0

        elif (
            self.footing_shape is FootingShape.SQUARE
            or self.footing_shape is FootingShape.CIRCULAR
        ):
            _sq = 1.2

        elif self.footing_shape is FootingShape.RECTANGULAR:
            _sq = 1 + 0.2 * self.width_2_length_ratio

        else:
            msg = ""
            raise TypeError(msg)

        return _sq

    @property
    def sgamma(self) -> float:
        r"""Returns ``Hansen`` shape factor :math:`s_\gamma`."""
        _sgamma: float

        if self.footing_shape is FootingShape.STRIP:
            _sgamma = 1.0

        elif self.footing_shape is FootingShape.SQUARE:
            _sgamma = 0.8

        elif self.footing_shape is FootingShape.CIRCULAR:
            _sgamma = 0.6

        elif self.footing_shape is FootingShape.RECTANGULAR:
            _sgamma = 1 - 0.4 * self.width_2_length_ratio

        else:
            msg = ""
            raise TypeError(msg)

        return _sgamma


@dataclass
class hansen_inclination_factors:
    cohesion: float
    footing_size: FootingSize
    beta: float
    total_vertical_load: float

    @property
    def ic(self) -> float:
        """Returns ``Hansen`` inclination factor :math:`i_c`."""
        x1 = (
            2
            * self.cohesion
            * self.footing_size.width
            * self.footing_size.length
        )
        return 1 - self.beta / x1

    @property
    def iq(self) -> float:
        """Returns ``Hansen`` inclination factor :math:`i_q`."""
        return 1 - (1.5 * self.beta) / self.total_vertical_load

    @property
    def igamma(self) -> float:
        r"""Returns ``Hansen`` inclination factor :math:`i_\gamma`."""
        return self.iq**2


class hansen_bearing_capacity:
    r"""Ultimate bearing capacity according to ``Hansen``.

    :param cohesion: Cohesion of foundation soil :math:`(kN/m^2)`
    :type cohesion: float
    :param soil_unit_weight: Unit weight of soil :math:`(kN/m^3)`
    :type soil_unit_weight: float
    :param foundation_size: Size of foundation
    :param friction_angle: Internal angle of friction (degrees)
    :type friction_angle: float
    :param beta: Inclination of the load on the foundation with respect to the vertical (degrees)
    :type beta: float
    :param total_vertical_load: Total vertical load on foundation
    :type total_vertical_load: float
    :param footing_shape: Shape of the footing
    :type footing_shape: float

    """

    def __init__(
        self,
        cohesion: float,
        soil_unit_weight: float,
        foundation_size: FoundationSize,
        soil_friction_angle: float,
        beta: float,
        total_vertical_load: float,
        footing_shape: FootingShape = FootingShape.SQUARE,
    ) -> None:
        self.cohesion = cohesion
        self.soil_unit_weight = soil_unit_weight
        self.foundation_size = foundation_size
        self.soil_friction_angle = soil_friction_angle
        self.beta = beta
        self.footing_shape = footing_shape
        self.total_vertical_load = total_vertical_load

        self.bearing_cpty_factors = hansen_bearing_capacity_factors(
            self.soil_friction_angle
        )
        self.depth_factors = hansen_depth_factors(self.foundation_size)
        self.shape_factors = hansen_shape_factors(
            self.foundation_size.footing_size, self.footing_shape
        )
        self.incl_factors = hansen_inclination_factors(
            self.cohesion,
            self.foundation_size.footing_size,
            self.beta,
            self.total_vertical_load,
        )

    def __call__(self) -> float:
        return self.ultimate()

    def ultimate(self) -> float:
        """Returns the ultimate bearing capacity according to ``Hansen``."""
        x1 = self.cohesion * self.nc * self.sc * self.dc * self.ic
        x2 = self.soil_unit_weight * self.foundation_size.depth
        x3 = self.nq * self.sq * self.dq * self.iq
        x4 = self.soil_unit_weight * self.foundation_size.width
        x5 = self.ngamma * self.sgamma * self.dgamma * self.igamma

        return x1 + (x2 * x3) + (0.5 * x4 * x5)

    @property
    def nc(self) -> float:
        return self.bearing_cpty_factors.nc

    @property
    def nq(self) -> float:
        return self.bearing_cpty_factors.nq

    @property
    def ngamma(self) -> float:
        return self.bearing_cpty_factors.ngamma

    @property
    def dc(self) -> float:
        return self.depth_factors.dc

    @property
    def dq(self) -> float:
        return self.depth_factors.dq

    @property
    def dgamma(self) -> float:
        return self.depth_factors.dgamma

    @property
    def sc(self) -> float:
        return self.shape_factors.sc

    @property
    def sq(self) -> float:
        return self.shape_factors.sq

    @property
    def sgamma(self) -> float:
        return self.shape_factors.sgamma

    @property
    def ic(self) -> float:
        return self.incl_factors.ic

    @property
    def iq(self) -> float:
        return self.incl_factors.iq

    @property
    def igamma(self) -> float:
        return self.incl_factors.igamma


@dataclass
class vesic_bearing_capacity_factors:
    soil_friction_angle: float

    @property
    def nc(self) -> float:
        """Returns ``Vesic`` bearing capacity factor :math:`N_c`."""
        return (1 / tan(self.soil_friction_angle)) * (self.nq - 1)

    @property
    def nq(self) -> float:
        """Returns ``Vesic`` bearing capacity factor :math:`N_q`."""
        x1 = tan(45 + self.soil_friction_angle / 2)
        x2 = exp(PI * tan(self.soil_friction_angle))

        return (x1**2) * (x2)

    @property
    def ngamma(self) -> float:
        r"""Returns ``Vesic`` bearing capacity factor :math:`N_\gamma`."""
        return 2 * (self.nq + 1) * tan(self.soil_friction_angle)


@dataclass
class vesic_depth_factors:
    soil_friction_angle: float
    foundation_size: FoundationSize

    @property
    def depth_2_width_ratio(self) -> float:
        return self.foundation_size.depth_2_width_ratio

    @property
    def dc(self) -> float:
        """Returns ``Vesic`` depth factor :math:`d_c`."""
        return 1 + 0.4 * self.depth_2_width_ratio

    @property
    def dq(self) -> float:
        """Returns ``Vesic`` depth factor :math:`d_q`."""
        x1 = 2 * tan(self.soil_friction_angle)
        x2 = (1 - sin(self.soil_friction_angle)) ** 2
        x3 = self.depth_2_width_ratio

        return 1 + (x1 * x2 * x3)

    @property
    def dgamma(self) -> float:
        r"""Returns ``Vesic`` depth factor :math:`d_\gamma`."""
        return 1.0


@dataclass
class vesic_shape_factors:
    soil_friction_angle: float
    footing_size: FootingSize
    footing_shape: FootingShape
    nq: float
    nc: float

    @property
    def width_2_length_ratio(self) -> float:
        return self.footing_size.width_2_length_ratio

    @property
    def sc(self) -> float:
        """Returns ``Vesic`` shape factor :math:`s_c`."""
        _sc: float

        if self.footing_shape is FootingShape.STRIP:
            _sc = 1.0

        elif (
            self.footing_shape is FootingShape.SQUARE
            or self.footing_shape is FootingShape.CIRCULAR
        ):
            _sc = 1 + (self.nq / self.nc)

        elif self.footing_shape is FootingShape.RECTANGULAR:
            _sc = 1 + self.width_2_length_ratio * (self.nq / self.nc)

        else:
            msg = ""
            raise TypeError(msg)

        return _sc

    @property
    def sq(self) -> float:
        """Returns ``Vesic`` shape factor :math:`s_q`."""
        _sq: float

        if self.footing_shape is FootingShape.STRIP:
            _sq = 1.0

        elif (
            self.footing_shape is FootingShape.SQUARE
            or self.footing_shape is FootingShape.CIRCULAR
        ):
            _sq = 1 + tan(self.soil_friction_angle)

        elif self.footing_shape is FootingShape.RECTANGULAR:
            _sq = 1 + self.width_2_length_ratio * tan(self.soil_friction_angle)

        else:
            msg = ""
            raise TypeError(msg)

        return _sq

    @property
    def sgamma(self) -> float:
        r"""Returns ``Vesic`` shape factor :math:`s_\gamma`."""
        _sgamma: float

        if self.footing_shape is FootingShape.STRIP:
            _sgamma = 1.0

        elif (
            self.footing_shape is FootingShape.SQUARE
            or self.footing_shape is FootingShape.CIRCULAR
        ):
            _sgamma = 0.6

        elif self.footing_shape is FootingShape.RECTANGULAR:
            _sgamma = 1 - 0.4 * (self.width_2_length_ratio)

        else:
            msg = ""
            raise TypeError(msg)

        return _sgamma


@dataclass
class vesic_inclination_factors:
    soil_friction_angle: float
    beta: float

    @property
    def ic(self) -> float:
        """Returns ``Vesic`` inclination factor :math:`i_c`."""
        return (1 - self.beta / 90) ** 2

    @property
    def iq(self) -> float:
        """Returns ``Vesic`` inclination factor :math:`i_q`."""
        return self.ic

    @property
    def igamma(self) -> float:
        r"""Returns ``Vesic`` inclination factor :math:`i_\gamma`."""
        return (1 - self.beta / self.soil_friction_angle) ** 2


class vesic_bearing_capacity:
    r"""Ultimate bearing capacity according to ``Vesic``.

    :param cohesion: Cohesion of foundation soil :math:`(kN/m^2)`
    :type cohesion: float
    :param unit_weight_of_soil: Unit weight of soil :math:`(kN/m^3)`
    :type unit_weight_of_soil: float
    :param foundation_size: Size of foundation
    :param friction_angle: Internal angle of friction (degrees)
    :type friction_angle: float
    ::param beta: Inclination of the load on the foundation with
                  respect to the vertical (degrees)
    :type beta: float
    :param total_vertical_load: total vertical load on foundation
    :type total_vertical_load: float
    :param footing_shape: Shape of the footing
    :type footing_shape: float
    """

    def __init__(
        self,
        cohesion: float,
        soil_unit_weight: float,
        foundation_size: FoundationSize,
        soil_friction_angle: float,
        beta: float,
        footing_shape: FootingShape = FootingShape.SQUARE,
    ) -> None:
        self.cohesion = cohesion
        self.soil_unit_weight = soil_unit_weight
        self.foundation_size = foundation_size
        self.soil_friction_angle = soil_friction_angle
        self.beta = beta
        self.footing_shape = footing_shape

        self.bearing_cpty_factors = vesic_bearing_capacity_factors(
            self.soil_friction_angle
        )
        self.depth_factors = vesic_depth_factors(
            self.soil_friction_angle, self.foundation_size
        )
        self.shape_factors = vesic_shape_factors(
            self.soil_friction_angle,
            self.foundation_size.footing_size,
            self.footing_shape,
            self.nq,
            self.nc,
        )
        self.incl_factors = vesic_inclination_factors(
            self.soil_friction_angle, self.beta
        )

    def __call__(self) -> float:
        return self.ultimate()

    def ultimate(self) -> float:
        r"""Returns the ultimate bearing capacity according to ``Hansen``."""
        x1 = self.cohesion * self.nc * self.sc * self.dc * self.ic
        x2 = self.soil_unit_weight * self.foundation_size.depth
        x3 = self.nq * self.sq * self.dq * self.iq
        x4 = self.soil_unit_weight * self.foundation_size.width
        x5 = self.ngamma * self.sgamma * self.dgamma * self.igamma

        return x1 + (x2 * x3) + (0.5 * x4 * x5)

    @property
    def nc(self) -> float:
        return self.bearing_cpty_factors.nc

    @property
    def nq(self) -> float:
        return self.bearing_cpty_factors.nq

    @property
    def ngamma(self) -> float:
        return self.bearing_cpty_factors.ngamma

    @property
    def dc(self) -> float:
        return self.depth_factors.dc

    @property
    def dq(self) -> float:
        return self.depth_factors.dq

    @property
    def dgamma(self) -> float:
        return self.depth_factors.dgamma

    @property
    def sc(self) -> float:
        return self.shape_factors.sc

    @property
    def sq(self) -> float:
        return self.shape_factors.sq

    @property
    def sgamma(self) -> float:
        return self.shape_factors.sgamma

    @property
    def ic(self) -> float:
        return self.incl_factors.ic

    @property
    def iq(self) -> float:
        return self.incl_factors.iq

    @property
    def igamma(self) -> float:
        return self.incl_factors.igamma

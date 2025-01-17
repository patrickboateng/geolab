from geolysis.bearing_capacity.ubc_4_soils import (
    SoilProperties,
    UltimateBearingCapacity,
)
from geolysis.foundation import FoundationSize
from geolysis.utils import (
    INF,
    PI,
    cos,
    cot,
    deg2rad,
    exp,
    isclose,
    round_,
    tan,
)

__all__ = [
    "TerzaghiUBC4StripFooting",
    "TerzaghiUBC4CircFooting",
    "TerzaghiUBC4SquareFooting",
    "TerzaghiUBC4RectFooting",
]


class TerzaghiBearingCapacityFactor:
    @classmethod
    @round_
    def n_c(cls, friction_angle: float) -> float:
        return (
            5.7
            if isclose(friction_angle, 0.0)
            else cot(friction_angle) * (cls.n_q(friction_angle) - 1)
        )

    @classmethod
    @round_
    def n_q(cls, friction_angle: float) -> float:
        return exp(
            (3 * PI / 2 - deg2rad(friction_angle)) * tan(friction_angle)
        ) / (2 * (cos(45 + friction_angle / 2)) ** 2)

    @classmethod
    @round_
    def n_gamma(cls, friction_angle: float) -> float:
        return (cls.n_q(friction_angle) - 1) * tan(1.4 * friction_angle)


class TerzaghiShapeFactor:
    @classmethod
    def s_c(cls) -> float:
        return 1.0

    @classmethod
    def s_q(cls) -> float:
        return 1.0

    @classmethod
    def s_gamma(cls) -> float:
        return 1.0


class TerzaghiDepthFactor:
    @classmethod
    def d_c(cls) -> float:
        return 1.0

    @classmethod
    def d_q(cls) -> float:
        return 1.0

    @classmethod
    def d_gamma(cls) -> float:
        return 1.0


class TerzaghiInclinationFactor:
    @classmethod
    def i_c(cls) -> float:
        return 1.0

    @classmethod
    def i_q(cls) -> float:
        return 1.0

    @classmethod
    def i_gamma(cls) -> float:
        return 1.0


class TerzaghiUltimateBearingCapacity(UltimateBearingCapacity):
    def __init__(
        self,
        soil_properties: SoilProperties,
        foundation_size: FoundationSize,
        water_level: float = INF,
        apply_local_shear: bool = False,
    ) -> None:
        super().__init__(
            soil_properties,
            foundation_size,
            water_level,
            apply_local_shear,
        )

    @property
    def n_c(self) -> float:
        r"""Bearing capacity factor :math:`N_c`.

        .. math:: N_c = \cot \phi (N_q - 1)
        """
        return TerzaghiBearingCapacityFactor.n_c(self.friction_angle)

    @property
    def n_q(self) -> float:
        r"""Bearing capacity factor :math:`N_q`.

        .. math::

            N_q = \dfrac{e^{(\frac{3\pi}{2} - \phi)\tan\phi}}
                  {2\cos^2(45 + \frac{\phi}{2})}
        """
        return TerzaghiBearingCapacityFactor.n_q(self.friction_angle)

    @property
    def n_gamma(self) -> float:
        r"""Bearing capacity factor :math:`N_{\gamma}`.

        .. math:: N_{\gamma} =  (N_q - 1) \tan(1.4\phi)
        """
        return TerzaghiBearingCapacityFactor.n_gamma(self.friction_angle)

    @property
    def s_c(self) -> float:
        """Shape factor :math:`s_c`."""
        return TerzaghiShapeFactor.s_c()

    @property
    def s_q(self) -> float:
        """Shape factor :math:`s_q`."""
        return TerzaghiShapeFactor.s_q()

    @property
    def s_gamma(self) -> float:
        r"""Shape factor :math:`s_{\gamma}`."""
        return TerzaghiShapeFactor.s_gamma()

    @property
    def d_c(self) -> float:
        """Depth factor :math:`d_c`."""
        return TerzaghiDepthFactor.d_c()

    @property
    def d_q(self) -> float:
        """Depth factor :math:`d_q`."""
        return TerzaghiDepthFactor.d_q()

    @property
    def d_gamma(self) -> float:
        r"""Depth factor :math:`d_{\gamma}`."""
        return TerzaghiDepthFactor.d_gamma()

    @property
    def i_c(self) -> float:
        """Inclination factor :math:`i_c`."""
        return TerzaghiInclinationFactor.i_c()

    @property
    def i_q(self) -> float:
        """Inclination factor :math:`i_q`."""
        return TerzaghiInclinationFactor.i_q()

    @property
    def i_gamma(self) -> float:
        r"""Inclination factor :math:`i_{\gamma}`."""
        return TerzaghiInclinationFactor.i_gamma()


class TerzaghiUBC4StripFooting(TerzaghiUltimateBearingCapacity):
    r"""Ultimate bearing capacity for strip footing on cohesionless
    soils according to ``Terzaghi 1943``.

    :param float soil_friction_angle: Internal angle of friction of soil
        material.
    :param float cohesion: Cohesion of soil material.
    :param float moist_unit_wgt: Moist (Bulk) unit weight of soil material.
    :param FoundationSize foundation_size: Size of foundation.
    :param float water_level: Depth of water below the ground surface.
    :param float local_shear_failure: Indicates if local shear failure is likely
        to occur therefore modifies the soil_friction_angle and cohesion of the
        soil material.
    :param float e: Deviation of the applied load from the center of the
        footing, also know as eccentricity.

    Notes
    -----
    Ultimate bearing capacity for strip footing is given by the formula:

    .. math:: q_u = cN_c + qN_q + 0.5 \gamma BN_{\gamma}

    Examples
    --------

    """

    @round_
    def bearing_capacity(self) -> float:
        """Ultimate bearing capacity of soil."""
        return (
            self._cohesion_term(1)
            + self._surcharge_term()
            + self._embedment_term(0.5)
        )


class TerzaghiUBC4CircFooting(TerzaghiUltimateBearingCapacity):
    r"""Ultimate bearing capacity for circular footing on cohesionless
    soils according to ``Terzaghi 1943``.

    :param float soil_friction_angle: Internal angle of friction of soil
        material.
    :param float cohesion: Cohesion of soil material.
    :param float moist_unit_wgt: Moist (Bulk) unit weight of soil material.
    :param FoundationSize foundation_size: Size of foundation.
    :param float water_level: Depth of water below the ground surface.
    :param float local_shear_failure: Indicates if local shear failure is likely
        to occur therefore modifies the soil_friction_angle and cohesion of the
        soil material.
    :param float e: Deviation of the applied load from the center of the
        footing, also know as eccentricity.

    Notes
    -----
    Ultimate bearing capacity for circular footing is given by the formula:

    .. math:: q_u = 1.3cN_c + qN_q + 0.3 \gamma BN_{\gamma}

    Examples
    --------

    """

    @round_
    def bearing_capacity(self) -> float:
        return (
            self._cohesion_term(1.3)
            + self._surcharge_term()
            + self._embedment_term(0.3)
        )


class TerzaghiUBC4RectFooting(TerzaghiUltimateBearingCapacity):
    r"""Ultimate bearing capacity for rectangular footing on cohesionless
    soils according to ``Terzaghi 1943``.

    :param float soil_friction_angle: Internal angle of friction of soil
        material.
    :param float cohesion: Cohesion of soil material.
    :param float moist_unit_wgt: Moist (Bulk) unit weight of soil material.
    :param FoundationSize foundation_size: Size of foundation.
    :param float water_level: Depth of water below the ground surface.
    :param float local_shear_failure: Indicates if local shear failure is likely
        to occur therefore modifies the soil_friction_angle and cohesion of the
        soil material.
    :param float e: Deviation of the applied load from the center of the
        footing, also know as eccentricity.

    Notes
    -----
    Ultimate bearing capacity for rectangular footing is given by the formula:

    .. math::

        q_u = \left(1 + 0.3 \dfrac{B}{L} \right) c N_c + qN_q
              + \left(1 - 0.2 \dfrac{B}{L} \right) 0.5 B \gamma N_{\gamma}

    Examples
    --------

    """

    @round_
    def bearing_capacity(self) -> float:
        f_w = self.foundation_size.width
        f_l = self.foundation_size.length
        coh_coef = 1 + 0.3 * (f_w / f_l)
        emb_coef = (1 - 0.2 * (f_w / f_l)) / 2.0
        return (
            self._cohesion_term(coh_coef)
            + self._surcharge_term()
            + self._embedment_term(emb_coef)
        )


class TerzaghiUBC4SquareFooting(TerzaghiUBC4RectFooting):
    r"""Ultimate bearing capacity for square footing on cohesionless
    soils according to ``Terzaghi 1943``.

    :param float soil_friction_angle: Internal angle of friction of soil
        material.
    :param float cohesion: Cohesion of soil material.
    :param float moist_unit_wgt: Moist (Bulk) unit weight of soil material.
    :param FoundationSize foundation_size: Size of foundation.
    :param float water_level: Depth of water below the ground surface.
    :param float local_shear_failure: Indicates if local shear failure is likely
        to occur therefore modifies the soil_friction_angle and cohesion of the
        soil material.

    Notes
    -----
    Ultimate bearing capacity for square footing is given by the formula:

    .. math:: q_u = 1.3cN_c + qN_q + 0.4 \gamma BN_{\gamma}

    Examples
    --------

    """

    def bearing_capacity(self):
        return super().bearing_capacity()

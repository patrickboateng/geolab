"""This module provides classes for SPT Data Analysis.

.. currentmodule:: geolab.bearing_capacity.spt
"""
from typing import Sequence

from geolysis import ERROR_TOLERANCE, GeotechEng
from geolysis.utils import isclose, log10, prod, round_, sqrt


@round_(precision=2)
def n_design(corrected_spt_nvalues: Sequence[float], t: bool = False) -> float:
    r"""Returns the weighted average of the corrected SPT N-values
    in the foundation influence zone.

    influence zone = :math:`D_f + 2B` or to a depth up to which soil
    types are approximately the same.

    B = width of foundation

    .. math::

        N_{design} = \dfrac{\sum_{i=1}^{n} \frac{N_i}{i^2}}{\sum_{i=1}^{n} \frac{1}{i^2}}

    - :math:`n` |rarr| number of layers in the influence zone.
    - :math:`N_i` |rarr| corrected N-value at ith layer from the
      footing base.

    .. note::

        Alternatively, for ease in calculation, the lowest N-value from
        the influence zone can be taken as the :math:`N_{design}` as
        suggested by ``Terzaghi & Peck (1948)``.

    :param Sequence[float] corrected_spt_nvalues:
        Corrected SPT N-values in the foundation influence zone
    :param bool t:
        A flag used to specify that the minimum value in `corrected_spt_nvalues`
        should be taken as the :py:func:`n_design`

    :return: weighted average of corrected SPT N-values
    :rtype: float
    """

    if len(corrected_spt_nvalues) == 0:
        return 0.0

    if t:
        return min(corrected_spt_nvalues)

    total = 0.0
    total_weights = 0.0

    for idx, corrected_spt_nvalue in enumerate(corrected_spt_nvalues, start=1):
        idx_weight = 1 / idx**2
        total += idx_weight * corrected_spt_nvalue
        total_weights += idx_weight

    return total / total_weights


class SPTCorrections:
    r"""Standard Penetration Test N-value correction for **Overburden
    Pressure** and **Dilatancy**.

    The available overburden pressure corrections are :meth:`skempton_opc_1986`,
    :meth:`bazaraa_peck_opc_1969`, :meth:`gibbs_holtz_opc_1957`,
    :meth:`peck_et_al_opc_1974`, and :meth:`liao_whitman_opc_1986`.

    :param float hammer_efficiency:
        hammer efficiency, defaults to 0.6
    :param float borehole_diameter_correction:
        borehole diameter correction, defaults to 1.0
    :param float sampler_correction:
        sampler correction, defaults to 1.0
    :param float rod_length_correction:
        rod Length correction, defaults to 0.75
    :param float eop:
        effective overburden pressure :math:`kN/m^2`
    """

    def __init__(
        self,
        *,
        hammer_efficiency: float = 0.6,
        borehole_diameter_correction: float = 1.0,
        sampler_correction: float = 1.0,
        rod_length_correction: float = 0.75,
        eop: float = 0.0,
    ):
        self.hammer_efficiency = hammer_efficiency
        self.borehole_diameter_correction = borehole_diameter_correction
        self.sampler_correction = sampler_correction
        self.rod_length_correction = rod_length_correction
        self.eop = eop

    def skempton_opc_1986(self, recorded_spt_nval: int) -> float:
        r"""Return the overburden pressure correction given by
        ``Skempton (1986).``

        .. math::

            C_N = \dfrac{2}{1 + 0.01044\sigma_o}

        :param int recorded_spt_nval:
        """
        spt_n60 = self.spt_n60(recorded_spt_nval)
        corr_spt = (2 / (1 + 0.01044 * self.eop)) * spt_n60

        return min(corr_spt, 2 * spt_n60)

    def bazaraa_peck_opc_1969(self, recorded_spt_nval: int) -> float:
        r"""Return the overburden pressure correction given by
        ``Bazaraa (1967)`` and also by ``Peck and Bazaraa (1969)``.

        It is one of the commonly used corrections.

        According to them:

        .. math::

            N_c &= \dfrac{4N_R}{1 + 0.0418 \cdot \sigma_o}, \, \sigma_o \lt 71.8kN/m^2

            N_c &= \dfrac{4N_R}{3.25 + 0.0104 \cdot \sigma_o}, \, \sigma_o \gt 71.8kN/m^2

            N_c &= N_R \, , \, \sigma_o = 71.8kN/m^2

        :param int recorded_spt_nval:
        """

        spt_n60 = self.spt_n60(recorded_spt_nval)
        std_pressure = 71.8

        if isclose(self.eop, std_pressure, rel_tol=ERROR_TOLERANCE):
            return spt_n60

        if self.eop < std_pressure:
            corrected_spt = 4 * spt_n60 / (1 + 0.0418 * self.eop)

        else:
            corrected_spt = 4 * spt_n60 / (3.25 + 0.0104 * self.eop)

        return min(corrected_spt, 2 * spt_n60)

    def gibbs_holtz_opc_1957(self, recorded_spt_nval: int) -> float:
        r"""Return the overburden pressure correction given by
        ``Gibbs and Holtz``.

        It was only as late as in ``1957`` that ``Gibbs and Holtz``
        suggested that corrections should be made for field ``SPT``
        values for depth. As the correction factor came to be considered
        only after ``1957``, all empirical data published before ``1957``
        like those by ``Terzaghi`` is for uncorrected values of ``SPT``.

        In granular soils, the overburden pressure affects the penetration
        resistance. If two soils having same relative density but different
        confining pressures are tested, the one with a higher confining
        pressure gives a higher penetration number. As the confining pressure
        in cohesionless soils increases with the depth, the penetration number
        for soils at shallow depths is underestimated and that at greater
        depths is overestimated. For uniformity, the N-values obtained from
        field tests under different effective overburden pressures are
        corrected to a standard effective overburden pressure.
        ``Gibbs and Holtz (1957)``recommend the use of the following equation
        for dry or moist clean sand. (:cite:author:`2003:arora`, p. 428)

        .. math::

            N_c = \dfrac{350}{\sigma_o + 70} \cdot N_R \, , \, \sigma_o \le 280kN/m^2

        .. note::

            :math:`\frac{N_c}{N_R}` should lie between 0.45 and 2.0, if
            :math:`\frac{N_c}{N_R}` is greater than 2.0, :math:`N_c` should be
            divided by 2.0 to obtain the design value used in finding the
            bearing capacity of the soil. (:cite:author:`2003:arora`, p. 428)

        :param int recorded_spt_nval:
        """

        std_pressure = 280

        if self.eop > std_pressure:
            msg = f"{self.eop} should be less than or equal to {std_pressure}"
            raise ValueError(msg)

        spt_n60 = self.spt_n60(recorded_spt_nval)

        corrected_spt = spt_n60 * (350 / (self.eop + 70))
        spt_ratio = corrected_spt / spt_n60

        if 0.45 < spt_ratio < 2.0:
            return corrected_spt

        corrected_spt = corrected_spt / 2 if spt_ratio > 2.0 else corrected_spt

        return min(corrected_spt, 2 * spt_n60)

    def peck_et_al_opc_1974(self, recorded_spt_nval: int) -> float:
        r"""Return the overburden pressure given by ``Peck (1974)``.

        .. math::

            (N_1)_{60} &= C_N \cdot N_{60} \le 2 \cdot N_{60}

            C_N &= 0.77\log\left(\frac{1905}{\sigma}\right)

        :math:`C_N` |rarr| *overburden pressure coefficient factor*

        :param int recorded_spt_nval:
        """
        std_pressure = 24

        if self.eop < std_pressure:
            msg = (
                f"{self.eop} should be greater than or equal to {std_pressure}"
            )

            raise ValueError(msg)

        spt_n60 = self.spt_n60(recorded_spt_nval)
        corrected_spt = 0.77 * log10(1905 / self.eop) * spt_n60

        return min(corrected_spt, 2 * spt_n60)

    def liao_whitman_opc_1986(self, recorded_spt_nval: int) -> float:
        r"""Return the overburden pressure given by ``Liao Whitman (1986)``.

        .. math::

            C_N = \sqrt{\frac{100}{\sigma}}

        :param int recorded_spt_nval:
        """
        spt_n60 = self.spt_n60(recorded_spt_nval)
        corrected_spt = sqrt(100 / self.eop) * spt_n60

        return min(corrected_spt, 2 * spt_n60)

    @round_(precision=2)
    def spt_n60(self, recorded_spt_nval: int) -> float:
        r"""Return SPT N-value corrected for 60% hammer efficiency.

        .. math::

            N_{60} = \dfrac{E_m \cdot C_B \cdot C_s \cdot C_R \cdot N}{0.6}

        .. note::

            The ``energy correction`` is to be applied irrespective of
            the type of soil.

        :param int recorded_spt_nval:
        """
        correction = prod(
            self.hammer_efficiency,
            self.borehole_diameter_correction,
            self.sampler_correction,
            self.rod_length_correction,
        )

        return (correction * recorded_spt_nval) / 0.6

    @round_(precision=2)
    def dilatancy_correction(self, recorded_spt_nval: int) -> float:
        r"""Returns the dilatancy spt correction.

        **Dilatancy Correction** is a correction for silty fine sands and
        fine sands below the water table that develop pore pressure which
        is not easily dissipated. The pore pressure increases the resistance
        of the soil hence the penetration number (N).
        (:cite:author:`2003:arora`)

        Correction of silty fine sands recommended by ``Terzaghi and Peck
        (1967)`` if :math:`N_{60}` exceeds 15.

        .. math::

            N_c &= 15 + \frac{1}{2}\left(N_{60} - 15\right) \, , \, N_{60} \gt 15

            N_c &= N_{60} \, , \, N_{60} \le 15

        :param int recorded_spt_nval:
        """

        spt_n60 = self.spt_n60(recorded_spt_nval)

        if spt_n60 <= 15:
            return spt_n60

        return 15 + 0.5 * (spt_n60 - 15)

    @round_(precision=2)
    def overburden_pressure_correction(
        self,
        recorded_spt_nval: int,
        eng: GeotechEng = GeotechEng.SKEMPTON,
    ) -> float:
        """Returns the overburden pressure spt correction.

        :param int recorded_spt_nval:

        :param GeotechEng eng:
            specifies the type of overburden pressure correction formula to use.
            Available values are ``GeotechEng.GIBBS``, ``GeotechEng.BAZARAA``,
            ``GeotechEng.PECK``, ``GeotechEng.LIAO``, and ``GeotechEng.SKEMPTON``
        """
        if eng is GeotechEng.GIBBS:
            corrected_spt = self.gibbs_holtz_opc_1957(recorded_spt_nval)

        elif eng is GeotechEng.BAZARAA:
            corrected_spt = self.bazaraa_peck_opc_1969(recorded_spt_nval)

        elif eng is GeotechEng.WOLFF:
            corrected_spt = self.peck_et_al_opc_1974(recorded_spt_nval)

        elif eng is GeotechEng.LIAO:
            corrected_spt = self.liao_whitman_opc_1986(recorded_spt_nval)

        elif eng is GeotechEng.SKEMPTON:
            corrected_spt = self.skempton_opc_1986(recorded_spt_nval)

        else:
            msg = f"{eng} is not a valid type for overburden pressure spt correction"
            raise TypeError(msg)

        return corrected_spt

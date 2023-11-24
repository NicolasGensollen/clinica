from pathlib import Path
from typing import Optional


def clinica_surfstat(
    input_dir: Path,
    output_dir: Path,
    tsv_file: Path,
    design_matrix: str,
    contrast: str,
    glm_type: str,
    group_label: str,
    freesurfer_home: Path,
    feature_label: str,
    surface_file: Optional[str] = None,
    fwhm: Optional[int] = 20,
    threshold_uncorrected_pvalue: Optional[float] = 0.001,
    threshold_corrected_pvalue: Optional[float] = 0.05,
    cluster_threshold: Optional[float] = 0.001,
) -> None:
    """This function mimics the previous function `clinica_surfstat`
    written in MATLAB and relying on the MATLAB package SurfStat.

    This implementation is written in pure Python and rely on the
    package brainstat for GLM modeling.

    Results, both plots and matrices, will be written in the location
    specified through `output_dir`.

    The names of the output files within `output_dir` follow the
    conventions:

        <ROOT>_<SUFFIX>.<EXTENSION>

    EXTENSION can be:

        - "mat": for storing matrices (this is mainly for backward
          compatibility with the previous MATLAB implementation of
          this function).
        - "json": for storing matrices in a more Pythonic way.
        - "png" for surface figures.

    SUFFIX can be:

        - "coefficients": relative to the model's beta coefficients.
        - "TStatistics": relative to the T-statistics.
        - "uncorrectedPValue": relative to the uncorrected P-values.
        - "correctedPValues": relative to the corrected P-values.
        - "FDR": Relative to the False Discovery Rate.

    ROOT can be:

        - For group comparison GLM with an interaction term:

            interaction-<contrast_name>_measure-<feature_label>_fwhm-<fwhm>

        - For group comparison GLM without an interaction term:

            group-<group_label>_<contrast_name>_measure-<feature_label>_fwhm-<fwhm>

        - For correlation GLM:

            group-<group_label>_correlation-<contrast_name>-<contrast_sign>_measure-<feature_label>_fwhm-<fwhm>

    Parameters
    ----------
    input_dir : Path
        The path to the input folder.

    output_dir : Path
        The path to the output folder for storing results.

    tsv_file : Path
        The path to the TSV file `subjects.tsv` which contains the
        necessary metadata to run the statistical analysis.

        .. warning::
            The column names need to be accurate because they
            are used to defined contrast and model terms.
            Please double check for typos.

    design_matrix : str
        The design matrix specified in string format.
        For example "1 + Label"

    contrast : str
        The contrast to be used in the GLM, specified in string format.

        .. warning::
            The contrast needs to be in the design matrix.

    glm_type : {"group_comparison", "correlation"}
        Type of GLM to run:
            - "group_comparison": Performs group comparison.
              For example "AD - ND".
            - "correlation": Performs correlation analysis.

    group_label : str
        The label for the group. This is used in the output file names
        (see main description of the function).

    freesurfer_home : Path
        The path to the home folder of Freesurfer.
        This is required to get the fsaverage templates.

    surface_file : str, optional
        The path to the surface file to analyze.
        Typically the cortical thickness.
        If `None`, the surface file will be the t1 freesurfer template.

    feature_label : str
        The label used for the measure. This is used in the output file
        names (see main description of the function).

    fwhm : int, optional
        The smoothing FWHM. This is used in the output file names.
        Default=20.

    threshold_uncorrected_pvalue : float, optional
        The threshold to be used with uncorrected P-values. Default=0.001.

    threshold_corrected_pvalue : float, optional
        The threshold to be used with corrected P-values. Default=0.05.

    cluster_threshold : float, optional
        The threshold to be used to declare clusters as significant. Default=0.05.
    """
    from clinica.utils.stream import cprint

    from ._utils import (
        build_thickness_array,
        get_average_surface,
        get_t1_freesurfer_custom_file_template,
        read_and_check_tsv_file,
    )
    from .models import GLMModelType, create_glm_model

    df_subjects = read_and_check_tsv_file(tsv_file)
    cprint(f"Pipeline will run on {len(df_subjects)} subjects.", lvl="info")
    surface_file: str = surface_file or get_t1_freesurfer_custom_file_template(
        input_dir
    )
    cprint(f"Using surface file: {surface_file}.", lvl="info")
    thickness = build_thickness_array(input_dir, surface_file, df_subjects, fwhm)
    cprint(f"Cortical thickness array loaded. Shape is {thickness.shape}.", lvl="info")

    # Load average surface template
    average_surface, average_mesh = get_average_surface(
        freesurfer_home / "subjects" / "fsaverage" / "surf"
    )

    # Build and run GLM model
    glm_model = create_glm_model(
        GLMModelType(glm_type),
        design_matrix,
        df_subjects,
        contrast,
        feature_label,
        group_label=group_label,
        fwhm=fwhm,
        threshold_uncorrected_pvalue=threshold_uncorrected_pvalue,
        threshold_corrected_pvalue=threshold_corrected_pvalue,
        cluster_threshold=cluster_threshold,
    )
    cprint(f"Fitting a {glm_type} GLM model...", lvl="info")
    glm_model.fit(thickness, average_surface)

    cprint(f"Saving model in {output_dir}.", lvl="info")
    glm_model.save_results(output_dir, ["json", "mat"])

    cprint(f"Saving plots in {output_dir}.", lvl="info")
    glm_model.plot_results(output_dir, ["nilearn_plot_surf_stat_map"], average_mesh)

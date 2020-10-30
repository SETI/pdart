import abc
import os
import os.path
import traceback
from typing import Optional

from pdart.pipeline.Directories import Directories
from pdart.pipeline.MarkerFile import BasicMarkerFile


class Stage(metaclass=abc.ABCMeta):
    def __init__(
        self,
        dirs: Directories,
        proposal_id: int,
        selected_suffixes: Optional[bool] = False,
    ) -> None:
        self._bundle_segment = f"hst_{proposal_id:05}"
        self._dirs = dirs
        self._proposal_id = proposal_id
        self._selected_suffixes = selected_suffixes

    ##############################

    def __call__(self) -> None:
        self.begin_transaction()
        try:
            self._run()
            self.commit_transaction()
        except Exception as e:
            self.rollback_transaction(e)

    def begin_transaction(self) -> None:
        pass

    def commit_transaction(self) -> None:
        pass

    def rollback_transaction(self, e: Exception) -> None:
        pass

    @abc.abstractmethod
    def _run(self) -> None:
        pass

    ##############################

    def working_dir(self) -> str:
        return self._dirs.working_dir(self._proposal_id)

    def mast_downloads_dir(self) -> str:
        return self._dirs.mast_downloads_dir(self._proposal_id)

    def primary_files_dir(self) -> str:
        return self._dirs.primary_files_dir(self._proposal_id)

    def documents_dir(self) -> str:
        return self._dirs.documents_dir(self._proposal_id)

    def archive_primary_deltas_dir(self) -> str:
        return self._dirs.archive_primary_deltas_dir(self._proposal_id)

    def archive_browse_deltas_dir(self) -> str:
        return self._dirs.archive_browse_deltas_dir(self._proposal_id)

    def archive_label_deltas_dir(self) -> str:
        return self._dirs.archive_label_deltas_dir(self._proposal_id)

    def archive_dir(self) -> str:
        return self._dirs.archive_dir(self._proposal_id)

    def deliverable_dir(self) -> str:
        return self._dirs.deliverable_dir(self._proposal_id)

    def deliverable_bundle_dir(self) -> str:
        return self._dirs.deliverable_bundle_dir(self._proposal_id)

    def manifest_dir(self) -> str:
        return self._dirs.manifest_dir(self._proposal_id)

    def validation_report_dir(self) -> str:
        return self._dirs.validation_report_dir(self._proposal_id)


class MarkedStage(Stage):
    def __init__(
        self,
        dirs: Directories,
        proposal_id: int,
        selected_suffixes: Optional[bool] = False,
    ) -> None:
        Stage.__init__(self, dirs, proposal_id, selected_suffixes)
        if not os.path.exists(self.working_dir()):
            os.makedirs(self.working_dir())
        self._marker_file = BasicMarkerFile(self.working_dir())

    def class_name(self) -> str:
        return type(self).__name__

    def __call__(self) -> None:
        marker_info = self._marker_file.get_marker()
        if marker_info and marker_info.state == "FAILURE":
            return
        Stage.__call__(self)

    def begin_transaction(self) -> None:
        self._marker_file.set_marker_info(self.class_name(), "running")

    def commit_transaction(self) -> None:
        self._marker_file.set_marker_info(self.class_name(), "success")

    def rollback_transaction(self, e: Exception) -> None:
        error_text = (
            f"EXCEPTION raised by {self._bundle_segment}, "
            f"stage {self.class_name()}: {e}\n"
            f"{traceback.format_exc()}"
        )

        print("****", error_text)
        self._marker_file.set_marker_info(self.class_name(), "failure", error_text)

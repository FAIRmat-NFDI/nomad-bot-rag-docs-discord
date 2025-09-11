
Uploading data in NOMAD can be done in two ways:

- By dragging-and-dropping your files into the `PUBLISH > Uploads` page: suitable for users who have a relatively small amount of data or who want to test [how the processing works](explanation_how_the_processing_works.md).
- By using the Python-based [NOMAD API](../glossary/glossary.md/#api): suitable for users who have larger datasets and need to automatize the upload.
- By using the shell command `curl` for sending files to the upload: suitable for users who have larger datasets and need to automatize the upload.

You can upload the files one by one or you can zip them in [`.zip`](https://copyrightservice.co.uk/reg/creating-zip-files) or `.tar.gz` formats to upload a larger amount of files at once.

We suggest you to visit and read the [References > Best Practices: preparing the data and folder structure](refs.md/#best-practices-preparing-folder-upload) page to see what are the best practices to organize data in a directory tree prior to upload it.


## Drag-and-drop uploads

On the top-left menu, click on `PUBLISH > Uploads`.

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="/assets/uploading_and_publishing/upload_menu.png" alt="Uploads page" width="90%" title="Uploads page.">
    </label>
</div>


You can then click on `CREATE A NEW UPLOAD` or try one of the example uploads by clicking in `ADD EXAMPLE UPLOADS` and selecting one of the multiple options. In our case, we use a zip file with some computational data.

You can drag-and-drop your files or click on the `CLICK OR DROP FILES` button to browse through your local directories.

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="/assets/uploading_and_publishing/gwupload.gif" alt="GW upload gif" width="90%" title="Creating a new upload with DFT+GW data.">
    </label>
</div>


After the files are uploaded, a **processing** is triggered. Visit [Explanation - how the processing works](explanation_how_the_processing_works.md) to gain further insight into the process.

You will receive an email when the upload processing is finished.


## NOMAD API uploads

<!--TODO by @JFRudzinski-->

!!! warning
    Under construction.


## Command-line uploads

!!! warning
    Under construction.


## Sections of the Uploads page

At the top of the uploads page, you can modify certain general metadata fields.

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="/assets/uploading_and_publishing/top_fields_uploads.png" alt="Top fields in uploads page." width="90%" title="Top fields in uploads page.">
    </label>
</div>

The name of the upload can be modify by clicking on the pen icon :fontawesome-solid-pen:. The other icons correspond to:

<!--Confirm with Lauri the icons-->
- :fontawesome-solid-user-group: _Manage members_: allows users to invite collaborators by defining co-authors and reviewers roles.
- :fontawesome-solid-cloud-arrow-down: _Download files_: downloads all files present in the upload.
- :fontawesome-solid-rotate-left: _Reload_: reloads the uploads page.
- :fontawesome-solid-rotate: _Reprocess_: triggers again the processing of the uploaded data.
- :fontawesome-solid-angle-left::fontawesome-solid-angle-right: _API_: generates a JSON response to use by the [NOMAD API](../glossary/glossary.md/#api). See [Querying and performing Data Science](../querying_and_performing_Data_Science/intro.md) for more information.
- :fontawesome-solid-trash: _Delete the upload_: deletes completely the upload.

The remainder of the uploads page is divided in 4 sections. The first section, _(1) Prepare and upload your files_, shows the files and folder structure in the upload. You can add a `README.md` in the root directory and its content will be shown above this section..

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="/assets/uploading_and_publishing/upload_files.png" alt="Uploaded files." width="90%" title="Uploaded files.">
    </label>
</div>

The second section, _(2) Process data_, shows the processed data and the generated [entries](../glossary/glossary.md/#entries) in NOMAD.

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="/assets/uploading_and_publishing/entries.png" alt="Processed entries." width="90%" title="Processed entries.">
    </label>
</div>

The third section, _(3) Edit author metadata_, allows users to edit certain metadata fields from all entries recognized in the upload. This includes _comments_, where you can add as much extra information as you want, _references_, where you can add a URL to your upload (e.g., an article DOI), and _datasets_, where you can create or add the uploaded data into a more general dataset (see [How-to publish data > Organizing data in datasets](howto_publish_data.md/#organize-data-in-datasets)).

<p align="center">
    <img src="/assets/uploading_and_publishing/edit_author_metadata.png" alt="Edit author metadata." width="50%" title="Edit author metadata.">
</p>

The final section, _(4) Publish_, lets the user to publish the data with or without an embargo. This will be explained more in detail in [How-to publish data](howto_publish_data.md).

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="/assets/uploading_and_publishing/publish.png" alt="Publish button." width="90%" title="Publish button.">
    </label>
</div>

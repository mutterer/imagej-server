/*
 * #%L
 * ImageJ server for RESTful access to ImageJ.
 * %%
 * Copyright (C) 2013 - 2016 Board of Regents of the University of
 * Wisconsin-Madison.
 * %%
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * #L%
 */

package net.imagej.server;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import io.dropwizard.testing.junit.ResourceTestRule;
import io.scif.services.DatasetIOService;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.ws.rs.client.Entity;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;

import net.imagej.Dataset;
import net.imagej.server.resources.ObjectsResource;

import org.glassfish.jersey.media.multipart.BodyPart;
import org.glassfish.jersey.media.multipart.FormDataContentDisposition;
import org.glassfish.jersey.media.multipart.FormDataMultiPart;
import org.glassfish.jersey.media.multipart.MultiPartFeature;
import org.junit.ClassRule;
import org.junit.Test;

/**
 * Test for {@link ObjectsResource}.
 * 
 * @author Leon Yang
 */
public class ObjectsResourceTest extends AbstractResourceTest {

	@ClassRule
	public static final ResourceTestRule resources = resourcesBuilder.addProvider(
		MultiPartFeature.class).addProvider(ObjectsResource.class).build();

	/**
	 * A integrated test for the workflow using IOResource:<br/>
	 * <li>upload file</li>
	 * <li>get IDs</li>
	 * <li>get ID</li>
	 * <li>remove ID</li>
	 * <li>retrieve file</li>
	 */
	@Test
	public void ioResource() {
		try {
			// Test uploadFile
			final String imgID = uploadFile("imgs/about4.tif");
			assertTrue(objectService.contains(imgID));

			// Test getIDs
			final String secondImg = uploadFile("imgs/about4.tif");
			assertTrue(objectService.contains(secondImg));
			assertTrue(!imgID.equals(secondImg));
			final List<String> ids = Arrays.asList(getIDs());
			assertTrue(ids.contains(imgID));
			assertTrue(ids.contains(secondImg));

			// Test getID
			assertEquals(getObject(imgID).getStatusInfo(), Status.OK);
			assertEquals(getObject(secondImg).getStatusInfo(), Status.OK);

			// Test removeID
			assertEquals(Status.OK, removeID(secondImg).getStatusInfo());
			assertEquals(Status.NOT_FOUND, retrieveFile(secondImg, "fmt")
				.getStatusInfo());

			// Test retrieveFile
			final File downloaded = retrieveFile(imgID, "tiff").readEntity(
				File.class);
			final Dataset ds = ctx.service(DatasetIOService.class).open(downloaded
				.getAbsolutePath());
			final Iterator<?> expectedItr = ((Iterable<?>) objectService.find(imgID)
				.getObject()).iterator();
			final Iterator<?> actualItr = ds.iterator();
			while (expectedItr.hasNext()) {
				assertTrue(actualItr.hasNext());
				assertEquals(expectedItr.next(), actualItr.next());
			}
			assertTrue(!actualItr.hasNext());
		}
		catch (IOException exc) {
			fail(exc.getMessage());
		}
	}

	/**
	 * Gets available IDs.
	 * 
	 * @return an array of IDs
	 */
	public String[] getIDs() {
		return resources.client().target("/objects").request().get(String[].class);
	}

	/**
	 * Gets the detail of an object given its ID.
	 * 
	 * @param id object ID
	 * @return response of request
	 */
	public Response getObject(final String id) {
		return resources.client().target("/objects/" + id).request().get();
	}

	/**
	 * Removes an object given its ID.
	 * 
	 * @param id object ID
	 * @return response of request
	 */
	public Response removeID(final String id) {
		return resources.client().target("/objects/" + id).request().delete();
	}

	/**
	 * Upload file to IOResource
	 * 
	 * @param file
	 * @return the object ID of that file
	 * @throws IOException
	 */
	public String uploadFile(final String file) throws IOException {
		final URL url = this.getClass().getClassLoader().getResource(file);
		try (final FormDataMultiPart multiPart = new FormDataMultiPart()) {
			multiPart.bodyPart(new BodyPart(url.openStream(),
				MediaType.MULTIPART_FORM_DATA_TYPE).contentDisposition(
					FormDataContentDisposition.name("file").fileName(file).build()));
			final String response = resources.client().register(
				MultiPartFeature.class).target("/objects/upload").request().post(Entity
					.entity(multiPart, multiPart.getMediaType()), String.class);
			final Matcher matcher = Pattern.compile("\\{\"id\":\"([^\"]+)\"\\}")
				.matcher(response);
			assertTrue(matcher.find());
			return matcher.group(1);
		}
	}

	/**
	 * Retrieve an object as a file
	 * 
	 * @param objectId object ID
	 * @param format format of the file to be saved
	 * @return object as a file
	 */
	public Response retrieveFile(final String objectId, final String format) {
		return resources.client().target("/objects/" + objectId + "/" + format)
			.request().get(Response.class);
	}
}